IFC_CONSTRUCTION_PROMPT = """
You are tasked to generate an specific Information Flow Card (IFC) for a random scenario.
The IFC identifies the sender, receiver, social relation, scenario, goal, information, inforamtion type, and common norms.
There are explaination for each field in the IFC:
1. Sender: A person who wants to achieve the goal.
2. Receiver: The person the sender wishes to communicate with.
3. Social Relation: The relationship between the sender and receiver.
4. Scenario: The context of the conversation.
5. Goal: The purpose of sending the information.
6. Information: Sender's information with the context, separated by semicolon.
7. Information Type: The type of the information field, separated by semicolon.
8. Common Norms: The norms that apply to the information being sent, separated by semicolon.
Your reponse should be a JSON dictionary, note that keep information short and concise with good consistency.
Examples:

# Example 1
{
    "sender": "Alice, a student who wants to apply for a PhD position",
    "receiver": "Dr. Smith, a professor specializing in AI",
    "social_relation": "Alice and Dr. Smith are strangers",
    "scenario": "Alice and Dr. Smith are at a conference poster session",
    "goal": "Alice wants to get a recommendation letter from Dr. Smith",
    "information": "Alice's research experience in machine learning; Alice's research interests in neural networks and AI ethics; Alice's contact information (email: alice@example.com);",
    "information_type": "research experience; research interests; contact information;,
    "common_norms": "It is ok to disclose research experience and interests in this scenario; contact information can be shared, but other personal details should be kept private."
}

# Example 2
{
    "sender": "John Doe, a parent who wants to discuss their child's progress",
    "receiver": "Mrs. Anderson, the child's teacher",
    "social_relation": "John and Mrs. Anderson are acquaintances through school meetings",
    "scenario": "Parent-teacher conference at the school",
    "goal": "John wants to understand how his child is performing academically and socially in class",
    "information": "The child's academic performance in math and reading; the child's social interactions with peers; areas where the child could improve, such as participation in class discussions;",
    "information_type": "academic performance; social behavior; suggestions for improvement;",
    "common_norms": "It is appropriate to discuss the child's academic and social progress in this setting with consent from both parties; confidentiality should be maintained regarding any information related to other students."
}

# Example 3
{
    "sender": "Jane Doe, a new employee",
    "receiver": "Mr. Johnson, the team manager",
    "social_relation": "Jane is a subordinate, and Mr. Johnson is her superior",
    "scenario": "Daily stand-up meeting in the office",
    "goal": "Jane wants to inform Mr. Johnson and the team about her progress and upcoming tasks",
    "information": "Current project status on the new website feature; tasks completed yesterday, including debugging and initial UI design; planned tasks for today, such as completing the remaining UI elements and starting on backend integration",
    "information_type": "project status; completed tasks; planned tasks",
    "common_norms": "Professionalism is required during updates; confidentiality must be maintained regarding internal projects and client information."
}
Your reponse:
"""

EXAMPLE = """
You are tasked to decide whether sharing user information satisfies user preferences to fill up the single data field for a webform with many other fields.
To add structure to your reasoning use Information Flow Card (IFC) that is rooted in the contextual integrity framework.
The IFC identifies the sender, receiver, information type, information subject and context, as well as the goals and applicable common norms.
You need to (1) build the short IFC card for the requested data given the form title, and (2) summarize the decision on whether it satisfies user preferences to fill up the data field using the IFC card and available context.
Note that some fields could be useful but not necessary, be conservative, assume there are other fields that can help with the form which would be asked in the next question.

User preferences:

1. The user prefers to share much less data than needed, so think twice if the task could be accomplished without this information.

2. The user lives in a country outside of United States and might not be aware of what data is necessary for US-specific purposes. Your goal is to make decisions that mirror that user's judgements.

Important: Your goal is to only provide data that satisfies user preferences even if the task won't be completed without this information.
"""

backup = """


"""