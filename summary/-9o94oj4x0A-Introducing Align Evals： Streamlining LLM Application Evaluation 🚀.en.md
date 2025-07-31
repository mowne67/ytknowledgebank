*   Building evaluators to score LLM applications is a crucial but difficult task.
*   A common method is using an LLM as a "judge" with a specific prompt, which requires extensive prompt tweaking.
*   LangSmith has launched a new feature called "align eval" to simplify this process.
*   "Align eval" allows users to create an evaluator by labeling data rather than just guessing at prompt changes.
*   The workflow for "align eval" consists of three main steps:
    1.  Collect a representative sample of application runs.
    2.  Have a human expert label these runs according to a specific criterion.
    3.  Iterate on an LLM judge prompt until its automated scores align with the human labels.
*   An example task is demonstrated: generating recipes where the titles should not contain superfluous adjectives (e.g., "easy," "perfectly").
*   To create the evaluator, a user adds a new evaluator "from labelled data" within a dataset.
*   A feedback key is created, such as "No superfluous adjectives."
*   The user selects an experiment and enters an "annotation queue" to label the runs.
*   In the queue, each run is scored (e.g., 1 for correct, 0 for incorrect) based on the defined criterion. For instance, "Classic beef and potato skillet" is labeled as having a superfluous adjective.
*   After labeling, the user enters the "evaluator playground" to craft the LLM judge prompt.
*   The prompt template is filled with instructions and placeholders for the application's output.
*   The "start alignment" function runs the LLM judge prompt across the human-labeled data and calculates an alignment percentage.
*   The interface allows for easy comparison between the LLM's scores and the human labels, highlighting disagreements.
*   Users can iterate on the prompt to improve alignment. For example, adding instructions that adjectives related to cooking methods ("grilled," "creamy") are not superfluous.
*   During iteration, it's also possible to change the underlying model for the LLM judge (e.g., switching to a more powerful model like GPT-4o Mini) to improve performance and reduce issues like hallucination.
*   Once a high alignment score (e.g., 89%) is achieved, the evaluator can be saved.
*   This saved evaluator can then be automatically run on new experiments to score the application's performance on that specific metric.
*   The system demonstrates how an initial prompt might score poorly (e.g., 22%) on the new evaluator.
*   By modifying the application's main prompt (e.g., adding "do not include any adjectives in the title that may be considered superfluous"), the performance score can be improved (e.g., to 77%).
*   This creates a full development loop: create an aligned evaluator, use it to test an application, improve the application based on the scores, and refine the evaluator as needed.
*   The "align eval" concept was inspired by research from Eugene Yan.
*   The feature is generally available for use in LangSmith.