*   Creating evaluators to score LLM applications is a crucial but often difficult part of development.
*   A common method for creating evaluators is using an LLM as a judge, which requires extensive prompt tweaking.
*   LangSmith has launched a new feature called "align eval" that allows users to create an evaluator by labeling data.
*   LangSmith is a platform for observing and evaluating LLM applications and works with or without the LangChain framework.
*   The "align eval" workflow consists of three steps:
    1.  Collect a representative sample of application runs.
    2.  Have a human expert label these runs based on a specific criterion.
    3.  Iterate on an evaluator prompt until its scores align with the human expert's labels.
*   A demonstration shows this process with a recipe generation application. The goal is to create an evaluator that scores whether generated recipe titles contain superfluous adjectives.
*   To begin, a user adds an evaluator from labeled data, defines a feedback key (e.g., "No superfluous adjectives"), and selects an experiment to annotate.
*   In the annotation queue, the user scores each run (e.g., 1 for meeting the criteria, 0 for not).
*   After labeling, the user moves to the "evaluator playground" to create the LLM-as-a-judge prompt.
*   The user writes grading instructions and specifies which parts of the application's run data (like the output content) should be fed into the prompt.
*   The "start alignment" function runs this new evaluator prompt over the labeled data and calculates an alignment percentage, showing how well the LLM's scores match the human labels.
*   The interface highlights mismatches, allowing the user to see where the evaluator is wrong and refine the prompt.
*   Prompt iteration can involve adding specific instructions, such as telling the LLM to only look at the title, or providing examples of what is and isn't considered superfluous (e.g., "grilled" is not superfluous).
*   If the prompt is still underperforming, the user can also change the underlying model for the evaluator (e.g., switching to a more powerful model like GPT-4o Mini) to improve results.
*   Once a high alignment score is achieved, the evaluator can be saved.
*   This saved evaluator can then be automatically run on new experiments. When the main application prompt is modified and re-run, the new outputs are scored against the custom evaluator.
*   This enables a continuous development loop: modify the application prompt, see the impact on the aligned evaluation score, and then if needed, go back and further refine the evaluator itself.
*   The feature was inspired by a project of the same name from independent researcher Eugene Yan.