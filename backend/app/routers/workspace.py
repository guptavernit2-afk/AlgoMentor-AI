from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel
import random

router = APIRouter(prefix="/api/workspace", tags=["Workspace"])

# --- Mock Data ---
MOCK_PROBLEM = {
    "id": "two-sum-1",
    "title": "Two Sum",
    "difficulty": "Easy",
    "topics": ["Array", "Hash Table"],
    "description": """
Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.

You may assume that each input would have ***exactly one solution***, and you may not use the same element twice.

You can return the answer in any order.

### Example 1:
```
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].
```

### Example 2:
```
Input: nums = [3,2,4], target = 6
Output: [1,2]
```

### Constraints:
* `2 <= nums.length <= 10^4`
* `-10^9 <= nums[i] <= 10^9`
* `-10^9 <= target <= 10^9`
* **Only one valid answer exists.**
    """,
    "starterCode": {
        "python": "class Solution:\n    def twoSum(self, nums: list[int], target: int) -> list[int]:\n        pass",
        "javascript": "/**\n * @param {number[]} nums\n * @param {number} target\n * @return {number[]}\n */\nvar twoSum = function(nums, target) {\n    \n};",
        "cpp": "class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        \n    }\n};"
    }
}

class EvaluateRequest(BaseModel):
    problem_id: str
    code: str
    language: str

class EvaluateResponse(BaseModel):
    status: str
    feedback: str
    is_optimal: bool

@router.get("/problems/recommendation")
def get_recommended_problem() -> Any:
    """
    Returns a mock problem recommended by the AI Mentor for today's session.
    """
    return MOCK_PROBLEM

@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate_code(req: EvaluateRequest) -> EvaluateResponse:
    """
    Mocks an AI Mentor evaluation of the submitted code.
    In the future, this will connect to an LLM API to provide real feedback.
    """
    # Simple heuristic to mock different responses based on code length
    code_len = len(req.code.strip())
    
    if code_len < 50:
        return EvaluateResponse(
            status="Incomplete",
            feedback="It looks like you haven't implemented the full solution yet. Don't forget you need to find two numbers that add up to the target!",
            is_optimal=False
        )
    
    # Very basic mock analysis
    if "for" in req.code and "in" in req.code and req.language == "python":
        if "{" in req.code or "dict" in req.code or "set" in req.code:
            return EvaluateResponse(
                status="Accepted",
                feedback="Excellent! You used a Hash Map to solve the problem in O(N) time complexity. This is the optimal approach.",
                is_optimal=True
            )
        else:
            return EvaluateResponse(
                status="Accepted",
                feedback="Your code looks correct, but it seems you might be using a brute force O(N^2) approach. Can you think of a way to do this in one pass using a Hash Map?",
                is_optimal=False
            )
            
    # Default positive response
    return EvaluateResponse(
        status="Accepted",
        feedback="Great job! Your logic seems solid. As a next step, consider discussing the time and space complexity.",
        is_optimal=True
    )
