from pathlib import Path

code = Path('C:/va-pipeline/applyflow.py').read_text(encoding='utf-8')

# Check for supabase check
has_check = "if supabase:" in code
print(f"Has supabase check: {has_check}")

# Show lines around supabase.table('jobs')
idx = code.find("supabase.table('jobs')")
if idx > 0:
    lines = code[max(0,idx-200):idx+100].split('\n')
    print(f"\nContext around supabase.table('jobs'):")
    for line in lines:
        print(f"  {line}")
else:
    print("supabase.table('jobs') not found")
