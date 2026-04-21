import json, os, subprocess, sys
from pathlib import Path

from litellm import completion

cR,cA,cT,cU,cE="\033[0m","\033[92m","\033[96m","\033[94m","\033[91m"

def say(p,c,s=""): t=str(s or ""); print(c+p+cR+t.replace("\n","\n"+" "*len(p))+cR)

class StdioMcpClient:
  def __init__(self,name,command,args,env):
    self.name=name; self.nextId=1
    merged=os.environ.copy(); merged.update({str(k):str(v) for k,v in (env or {}).items()})
    self.proc=subprocess.Popen([command,*args],stdin=subprocess.PIPE,stdout=subprocess.PIPE,env=merged,text=True,bufsize=1)
    self.stdin=self.proc.stdin; self.stdout=self.proc.stdout

  def request(self,method,params=None):
    rid=self.nextId; self.nextId+=1
    req={"jsonrpc":"2.0","id":rid,"method":method}
    if params is not None: req["params"]=params
    self.stdin.write(json.dumps(req,ensure_ascii=False,separators=(",",":"))+"\n"); self.stdin.flush()
    while True:
      line=self.stdout.readline()
      if not line: raise RuntimeError(self.name+": no response")
      if not line.strip(): continue
      payload=json.loads(line)
      if payload.get("id")!=rid: continue
      if payload.get("error"): raise RuntimeError(str(payload["error"]))
      return payload.get("result")

  def initialize(self):
    self.request("initialize",{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"quecto-agent","version":"0.0.0"}})
    self.stdin.write('{"jsonrpc":"2.0","method":"notifications/initialized"}\n'); self.stdin.flush()

  def close(self):
    try: self.proc.terminate()
    except Exception: pass

def execTool(args:str) -> str:
  data=json.loads(args or "{}"); cmd=str(data.get("cmd") or "")
  if not cmd: return "Error: cmd required"
  r=subprocess.run(cmd, shell=True, capture_output=True, text=True)
  out=(r.stdout or "")+(r.stderr or "")
  return out if r.returncode == 0 else f"Error: exit {r.returncode}\n{out}"

if __name__=="__main__":
  a=sys.argv[1:]; model=os.getenv("MODEL") or "gpt-5.4"
  for i,v in enumerate(a[:-1]):
    if v in ("-m","--model"): model=a[i+1]

  agentsText=Path("AGENTS.md").read_text().strip()
  skillNames=sorted(d.name for d in (Path(".agents")/"skills").iterdir() if (d/"SKILL.md").is_file())
  skillsText="\n\n".join(((Path(".agents")/"skills"/n/"SKILL.md").read_text().strip()) for n in skillNames)
  servers=json.loads(Path("mcp.json").read_text())["mcpServers"]

  mcpClients={}
  toolSpecs=[{"type":"function","function":{"name":"exec","description":"Run a shell command.","parameters":{"type":"object","properties":{"cmd":{"type":"string"}}}}}]
  for serverName,serverCfg in servers.items():
    client=StdioMcpClient(serverName,serverCfg["command"],serverCfg.get("args") or [],serverCfg.get("env")); client.initialize()
    mcpClients[serverName]=client
    for tool in (client.request("tools/list") or {}).get("tools") or []:
      full=f"mcp_{serverName}__{tool['name']}"
      toolSpecs.append({"type":"function","function":{"name":full,"description":tool.get("description") or "","parameters":tool["inputSchema"]}})

  systemPrompt="You are a terminal-based agent.\nSkills live at ./.agents/skills/*/SKILL.md.\n\nAGENTS.md:\n"+agentsText+"\n\nSkills:\n"+skillsText
  messages=[{"role":"system","content":systemPrompt}]
  say("Agent: ",cA,"Skills: "+(", ".join(skillNames) if skillNames else "(none)")+" | MCP: "+(", ".join(mcpClients) if mcpClients else "(none)"))
  while True:
    try: user=input(cU+"You: "+cR)
    except (EOFError, KeyboardInterrupt): break
    text=user.lower()
    messages.append({"role":"user","content":user})
    if "tool" in text and any(keyword in text for keyword in ("have","access","available")):
      listing="\n".join(t["function"]["name"] for t in toolSpecs)
      say("Agent: ",cA,listing); messages.append({"role":"assistant","content":listing}); continue
    while True:
      try:
        r=completion(model=model,messages=messages,tools=toolSpecs)
        message=r.model_dump()["choices"][0]["message"]
      except Exception as e: say("Agent: ",cE,str(e)); break
      if message.get("content"): say("Agent: ",cA,message["content"])
      messages.append(message); tool_calls=message.get("tool_calls") or ()
      if not tool_calls: break
      for call in tool_calls:
        f=call["function"]; name=f["name"]; args=f.get("arguments") or "{}"
        say("Tool: ",cT,f"{name}({args})")
        try:
          if name=="exec": out=execTool(args)
          else:
            serverName,toolName=name[4:].split("__",1)
            result=mcpClients[serverName].request("tools/call",{"name":toolName,"arguments":json.loads(args or "{}")})
            out=result if isinstance(result,str) else json.dumps(result,ensure_ascii=False,separators=(",",":"))
        except Exception as e:
          out=f"Error: {e}"
        messages.append({"role":"tool","tool_call_id":call["id"],"content":out})

  for client in mcpClients.values():
    try: client.close()
    except Exception: pass
