
INCLUDE_TERMS = [
    "fair",
    "requirement",
    "equal",
    "equity",
    "bias",
    "test",
    "metric"
]

EXCLUDE_TERMS = [
]

def filter(title_str):
    title = title_str.lower()
    include = False
    #exclude terms
    for term in EXCLUDE_TERMS:
        if term.lower() in title:
            return "EXCLUDE"
    #include terms
    for term in INCLUDE_TERMS:
        if term.lower() in title:
            include = True
            
    
print(filter("How is it that AI can become biased, and what are the proposals to mitigate this?"))
    