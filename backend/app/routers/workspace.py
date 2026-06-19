from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel
import random

router = APIRouter(prefix="/api/workspace", tags=["Workspace"])

# --- Mock Database ---
MOCK_PROBLEMS_DB = {
    "two-sum-1": {
        "id": "two-sum-1",
        "title": "Two Sum",
        "difficulty": "Easy",
        "topics": ["Array", "Hash Table"],
        "description": "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.\n\nYou may assume that each input would have ***exactly one solution***, and you may not use the same element twice.\n\nYou can return the answer in any order.\n\n### Example 1:\n```\nInput: nums = [2,7,11,15], target = 9\nOutput: [0,1]\nExplanation: Because nums[0] + nums[1] == 9, we return [0, 1].\n```\n\n### Constraints:\n* `2 <= nums.length <= 10^4`\n* `-10^9 <= nums[i] <= 10^9`\n* `-10^9 <= target <= 10^9`\n* **Only one valid answer exists.**",
        "starterCode": {
            "python": "class Solution:\n    def twoSum(self, nums: list[int], target: int) -> list[int]:\n        pass",
            "javascript": "/**\n * @param {number[]} nums\n * @param {number} target\n * @return {number[]}\n */\nvar twoSum = function(nums, target) {\n    \n};",
            "cpp": "class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        \n    }\n};"
        }
    },
    "valid-palindrome-2": {
        "id": "valid-palindrome-2",
        "title": "Valid Palindrome",
        "difficulty": "Easy",
        "topics": ["Two Pointers", "String"],
        "description": "A phrase is a **palindrome** if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward.\n\nGiven a string `s`, return `true` if it is a **palindrome**, or `false` otherwise.\n\n### Example 1:\n```\nInput: s = \"A man, a plan, a canal: Panama\"\nOutput: true\nExplanation: \"amanaplanacanalpanama\" is a palindrome.\n```\n\n### Constraints:\n* `1 <= s.length <= 2 * 10^5`\n* `s` consists only of printable ASCII characters.",
        "starterCode": {
            "python": "class Solution:\n    def isPalindrome(self, s: str) -> bool:\n        pass",
            "javascript": "/**\n * @param {string} s\n * @return {boolean}\n */\nvar isPalindrome = function(s) {\n    \n};",
            "cpp": "class Solution {\npublic:\n    bool isPalindrome(string s) {\n        \n    }\n};"
        }
    },
    "subarray-sum-3": {
        "id": "subarray-sum-3",
        "title": "Subarray Sum Equals K",
        "difficulty": "Medium",
        "topics": ["Array", "Hash Table", "Prefix Sum"],
        "description": "Given an array of integers `nums` and an integer `k`, return the total number of subarrays whose sum equals to `k`.\n\nA subarray is a contiguous **non-empty** sequence of elements within an array.\n\n### Example 1:\n```\nInput: nums = [1,1,1], k = 2\nOutput: 2\n```\n\n### Constraints:\n* `1 <= nums.length <= 2 * 10^4`\n* `-1000 <= nums[i] <= 1000`\n* `-10^7 <= k <= 10^7`",
        "starterCode": {
            "python": "class Solution:\n    def subarraySum(self, nums: list[int], k: int) -> int:\n        pass",
            "javascript": "/**\n * @param {number[]} nums\n * @param {number} k\n * @return {number}\n */\nvar subarraySum = function(nums, k) {\n    \n};",
            "cpp": "class Solution {\npublic:\n    int subarraySum(vector<int>& nums, int k) {\n        \n    }\n};"
        }
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
    return MOCK_PROBLEMS_DB["two-sum-1"]

@router.get("/problems/{problem_id}")
def get_problem(problem_id: str) -> Any:
    """
    Returns a specific problem from the DB.
    """
    # Return requested or fallback to two-sum
    return MOCK_PROBLEMS_DB.get(problem_id, MOCK_PROBLEMS_DB["two-sum-1"])

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
