import importlib.metadata

def write_requirements(filename=r"C:\Test-Kees\requirements.txt"):
    # 1. Fetch all installed distributions
    dists = importlib.metadata.distributions()
    
    # 2. Extract and format package metadata
    requirements = []
    for dist in dists:
        name = dist.metadata['Name']
        version = dist.version
        requirements.append(f"{name}=={version}")
    
    # 3. Sort and write to the file
    with open(filename, "w", encoding="utf-8") as f:
        for req in sorted(requirements):
            f.write(req + "\n")
    
    print(f"Successfully wrote {len(requirements)} packages to {filename}")

if __name__ == "__main__":
    write_requirements()
