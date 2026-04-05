import sys, json
raw = sys.stdin.read()
d = json.loads(raw)
app = d.get("app", "unknown")
count = d.get("count", 0)
print(f"app: {app}, elements: {count}")
for e in d.get("elements", [])[:20]:
    eid = e.get("id", "")
    role = e.get("role", "")
    label = e.get("label", "")
    value = e.get("value", "")
    print(f"  {eid} {role} label={label} value={value}")
