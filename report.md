### 1. Business Use Case
- This project aims to automatically convert unstructured meeting records into structured action items. The main users are project managers, team leaders, and other business personnel who need to quickly extract task and decision information from meetings. 
- The system takes the original meeting records as input and outputs structured content, which includes: decision matters, action items (including the responsible person and the deadline), as well as unresolved issues. This task has practical value because meeting records are usually incomplete and ambiguous, and manual sorting is costly and prone to errors.

### 2. Model Selection
- This project uses the Gemini API (gemini-2.5-flash). The reason for choosing this model is that it achieves a good balance between response speed and the quality of structured output, making it suitable for conducting multiple-round prompt iteration experiments. 
- This project did not compare with other models. From the experimental results, this model performs well in structured information extraction, but it is highly dependent on prompts, especially when dealing with ambiguous or missing information.

### 3. Baseline vs. Final Design Comparison
### Prompt Iteration Comparison (Simplified)

| Case | Initial | Revision 1 | Revision 2 |
|------|--------|------------|------------|
| **Case 1: Normal** | decisions: 2<br>action_items: 1 (Sarah, next Monday)<br>open_questions: none | Removed incorrect decision ("launch campaign") | Added open_question: "launch campaign" (more conservative) |
| **Case 2: Multiple Actions** | 2 action_items correctly extracted | No significant change | Added open_question about strategy |
| **Case 3: Missing Info** | owner: Unassigned<br>deadline: TBD | Standardized to "Not specified"<br>Added open_question | No significant change |
| **Case 4: No Actions** | No output (correct) | No change | No change |
| **Case 5: Ambiguous** | All treated as open_questions | Incorrectly converted one task into action_item | Correctly reverted to all open_questions (reduced hallucination) |

- The assessment is based on 5 fixed test cases, covering normal, boundary and high-risk scenarios.
In the normal version (Case 1), both iterations of the promotion process enabled the model's output to become progressively more accurate.
- During the processing of multiple actions (Case 2), the model was ultimately able to distinguish open questions.
- When information was incomplete (Case 3), the model was able to ensure that the missing items were clearly displayed.
- When information was extremely incomplete (Case 4), the model did not output any content, and this remained the same even after iterations.
- In cases of high ambiguity (Case 5), the model's output was not very stable. The same problem, when using prompts of different levels of completeness, the classification accuracy did not gradually improve as the prompt became more complete.

##### Initial Prompt
The initial prompt can produce correct results in simple scenarios. However, there is a problem where the "discussion content" is mistakenly identified as a "decision".

##### Revision 1
Revision 1 enhanced the consistency of the output structure by adding rule constraints. However, in high levels of ambiguity, there is still the issue of mistaking ambiguous suggestions for action items. 

##### Revision 2
Revision 2 introduces stricter constraints, further enhancing reliability, but the model becomes more conservative. The model has become more conservative.

### 4. Limitations and Need for Human Review
The current prototype still has problems such as difficulty in distinguishing implicit decisions from ordinary discussions, being overly conservative in ambiguous scenarios, being highly dependent on prompt rules, and lacking deep semantic understanding. Therefore, in scenarios where information is incomplete or ambiguous, and when key business decisions are involved, human intervention for review is still necessary.
### 5. Deployment Recommendation
- This AI model is suitable as an auxiliary tool for meeting records, but it cannot rely solely on the model.
- If we need to deploy the model, perhaps we will need more manual reviews, or use some vetted cases for training the model. And optimize the prompt in combination with the conference scenario.

