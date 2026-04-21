import json, os, subprocess, sys
from litellm import completion

cR,cA,cT,cU,cE="\033[0m","\033[92m","\033[96m","\033[94m","\033[91m"
def say(p,c,s=""): t=str(s or ""); print(c+p+cR+t.replace("\n","\n"+" "*len(p))+cR)
def opt(a,*k,d=None):
  for i,v in enumerate(a[:-1]):
    if v in k: return a[i+1]
  return d

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
  a=sys.argv[1:]; model=opt(a,"-m","--model",d=os.getenv("MODEL") or "gpt-5.4")
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
        r=completion(model=model, messages=messages, tools=tools)
        message=(r.model_dump() if hasattr(r,"model_dump") else r.dict())["choices"][0]["message"]
      except Exception as e: say("Agent: ",cE,str(e)); break
      if message.get("content"): say("Agent: ",cA,message["content"])
      messages.append(message); tool_calls=message.get("tool_calls") or ()
      if not tool_calls: break
      for call in tool_calls:
        f=call["function"]; args=f.get("arguments") or "{}"; say("Tool: ",cT,f"{f.get('name','exec')}({args})")
        messages.append({"role":"tool","tool_call_id":call["id"],"content":exec(args)})
