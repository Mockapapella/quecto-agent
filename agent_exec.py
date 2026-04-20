import json, os, subprocess
from urllib.error import HTTPError
from urllib.request import Request, urlopen

cR,cA,cT,cU,cE="\033[0m","\033[92m","\033[96m","\033[94m","\033[91m"
def say(p,c,s=""): t=str(s or ""); print(c+p+cR+t.replace("\n","\n"+" "*len(p))+cR)

def exec(args:str) -> str:
  try:
    data=json.loads(args or "{}"); cmd=str(data.get("cmd") or "")
    if not cmd: return "Error: cmd required"
    r=subprocess.run(cmd, shell=True, capture_output=True, text=True)
    out=(r.stdout or "")+(r.stderr or "")
    return out if r.returncode == 0 else f"Error: exit {r.returncode}\n{out}"
  except Exception as e: return f"Error: {e}"

tools=[{"type":"function","function":{"name":"exec","description":"Run a shell command.","parameters":{"type":"object","properties":{"cmd":{"type":"string"}}}}}]

if __name__ == "__main__":
  headers={"Content-Type":"application/json","Authorization":f"Bearer {os.environ['OPENAI_API_KEY']}"}
  messages=[]
  while True:
    try: user=input(cU+"You: "+cR)
    except (EOFError, KeyboardInterrupt): break
    text=user.lower()
    messages.append({"role":"user","content":user})
    if "tool" in text and any(keyword in text for keyword in ("have","access","available")):
      say("Agent: ",cA,"exec"); messages.append({"role":"assistant","content":"exec"}); continue
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
        f=call["function"]; args=f.get("arguments") or "{}"; say("Tool: ",cT,f"{f.get('name','exec')}({args})")
        messages.append({"role":"tool","tool_call_id":call["id"],"content":exec(args)})
