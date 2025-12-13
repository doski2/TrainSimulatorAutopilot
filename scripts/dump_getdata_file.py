from pathlib import Path

p = Path(r"C:\temp\GetData_test.txt")
print("File exists:", p.exists())
print("Raw lines:")
for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(True)):
    print(i, repr(line))
