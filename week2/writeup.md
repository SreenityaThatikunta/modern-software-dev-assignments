# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt: 
```
Implement TODO 1 in week2/assignment.md. Analyze the existing heuristic
extract_action_items() function and add extract_action_items_llm() using Ollama.
Use structured JSON output, make the model configurable, keep the existing
heuristic extractor unchanged, and validate the LLM response before returning it.
``` 

Generated Code Snippets:
```
week2/app/services/extract.py: L21-L33, L84-L124
```

### Exercise 2: Add Unit Tests
Prompt: 
```
Implement TODO 2 in week2/assignment.md. Add unit tests for
extract_action_items_llm() covering bullet-list input, keyword-prefixed input,
empty input, and cleanup of duplicate model output. Mock Ollama so the tests
are deterministic and do not require a locally running model.
``` 

Generated Code Snippets:
```
week2/tests/test_extract.py: L22-L70
```

### Exercise 3: Refactor Existing Code for Clarity
Prompt: 
```
Implement TODO 3 in week2/assignment.md. Refactor the backend around explicit
Pydantic request and response schemas, a database layer that returns typed
records and closes connections reliably, FastAPI lifespan initialization, and
consistent validation and not-found errors. Preserve existing feature behavior
and verify the API with an isolated SQLite database.
``` 

Generated/Modified Code Snippets:
```
week2/app/schemas.py: L1-L58
week2/app/db.py: L1-L145
week2/app/main.py: L1-L36
week2/app/routers/notes.py: L1-L27
week2/app/routers/action_items.py: L1-L47
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: 
```
Implement TODO 4 in week2/assignment.md. Add an endpoint that performs LLM
action-item extraction, an endpoint that lists all notes, and frontend controls
for both operations. Reuse the existing API schemas, display failures clearly,
and render returned note and action-item text safely.
``` 

Generated Code Snippets:
```
week2/app/services/extract.py: L84-L106
week2/app/routers/action_items.py: L23-L61
week2/app/routers/notes.py: L21-L23
week2/frontend/index.html: L24-L115
```


### Exercise 5: Generate a README from the Codebase
Prompt: 
```
Implement TODO 5 in week2/assignment.md. Analyze the completed Week 2 codebase
and create a README covering the project overview, standard-venv setup and run
instructions, Ollama configuration, API endpoints, frontend behavior, project
layout, and tests. Ensure the documentation matches the currently running API.
``` 

Generated Code Snippets:
```
week2/README.md: L1-L120
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope.
