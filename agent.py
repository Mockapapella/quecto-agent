import json, os
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

base = Path.cwd().resolve()
cR,cA,cT,cU,cE="\033[0m","\033[92m","\033[96m","\033[94m","\033[91m"
def say(p,c,s=""):
  t=str(s or ""); print(c+p+cR+t.replace("\n","\n"+" "*len(p))+cR)

def fs(args:str) -> str:
  try:
    data=json.loads(args or "{}"); path=(base/Path(data.get("path") or ".")).resolve()
    if not path.is_relative_to(base): return "Error: path must stay within working directory"
    if (new:=data.get("new_str")) is not None:
      path.parent.mkdir(parents=True, exist_ok=True); path.write_text(str(new), encoding="utf-8"); return "OK"
    return "\n".join(sorted(e.name for e in path.iterdir())) if path.is_dir() else path.read_text(encoding="utf-8", errors="replace")
  except Exception as e: return f"Error: {e}"

tools=[{"type":"function","function":{"name":"fs","description":"List/read/write within the working directory.","parameters":{"type":"object","properties":{"path":{"type":"string"},"new_str":{"type":"string"}}}}}]

if __name__ == "__main__":
  headers={"Content-Type":"application/json","Authorization":f"Bearer {os.environ['OPENAI_API_KEY']}"}
  messages=[]
  while True:
    try: user=input(cU+"You: "+cR)
    except (EOFError, KeyboardInterrupt): break
    text=user.lower()
    messages.append({"role":"user","content":user})
    if "tool" in text and any(keyword in text for keyword in ("have","access","available")):
      say("Agent: ",cA,"fs"); messages.append({"role":"assistant","content":"fs"}); continue
    while True:
      try:
        with urlopen(Request("https://api.openai.com/v1/chat/completions", data=json.dumps({"model":"gpt-5.4","messages":messages,"tools":tools}).encode("utf-8"), headers=headers), timeout=60) as res:
          message=json.loads(res.read())["choices"][0]["message"]
      except HTTPError as e: say("Agent: ",cE,e.read().decode("utf-8", errors="replace")); break
      except Exception as e: say("Agent: ",cE,str(e)); break
      if message.get("content"): say("Agent: ",cA,message["content"])
      messages.append(message); tool_calls=message.get("tool_calls") or ()
      if not tool_calls: break
      for call in tool_calls:
        f=call["function"]; name,args=f.get("name","fs"),f.get("arguments") or "{}"
        result=fs(args); say("Tool: ",cT,f"{name}({args})"+(f" -> {result}" if result.startswith("Error:") else ""))
        messages.append({"role":"tool","tool_call_id":call["id"],"content":result})
