## Case 1: Normal Case
### Input
- Discussed launching new marketing campaign
- Sarah will prepare draft by next Monday
- Team agreed to increase budget by 10%
### Expected Output
- Identify decision: budget increase
- Extract action item: prepare draft
- Correctly assign owner (Sarah)
- Correctly identify deadline (next Monday)


## Case 2: Multiple Action Items
### Input
- John will finalize the report
- Emily will review the report
- Deadline for both is Friday
- Discussed improving customer retention strategy
### Expected Output
- Extract two action items
- Assign correct owners (John, Emily)
- Assign shared deadline (Friday)
- Separate discussion (strategy) from action items


## Case 3: Missing Information
### Input
- Need to update the dashboard
- Someone should check data accuracy
- Timeline unclear
### Expected Output
- Extract action items
- Mark owner as "Not specified"
- Mark deadline as "Not specified"
- Avoid guessing missing information


## Case 4: No Clear Action Items
### Input
- Discussed company vision for next year
- Talked about market trends
- No specific tasks assigned
### Expected Output
- Recognize no actionable tasks
- Output should clearly state no action items
- Avoid hallucinating tasks or owners



## Case 5: Ambiguous / High Hallucination Risk
### Input
- Maybe update the pricing model?
- Consider revising onboarding process
- Alex mentioned something about timeline
### Expected Output
- Identify uncertainty in statements
- Avoid turning suggestions into confirmed action items
- Do not assign owner or deadline unless explicitly stated
- Highlight ambiguity or open questions