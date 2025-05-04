# #### What this tests ####
# #    This tests calling mishikallm.max_budget by making back-to-back gpt-4 calls
# # commenting out this test for circle ci, as it causes other tests to fail, since mishikallm.max_budget would impact other mishikallm imports
# import sys, os, json
# import traceback
# import pytest

# sys.path.insert(
#     0, os.path.abspath("../..")
# )  # Adds the parent directory to the system path
# import mishikallm
# # mishikallm.set_verbose = True
# from mishikallm import completion, BudgetExceededError

# def test_max_budget():
#     try:
#         mishikallm.max_budget = 0.001 # sets a max budget of $0.001

#         messages = [{"role": "user", "content": "Hey, how's it going"}]
#         response = completion(model="gpt-4", messages=messages, stream=True)
#         for chunk in response:
#             continue
#         print(mishikallm._current_cost)
#         completion(model="gpt-4", messages=messages, stream=True)
#         mishikallm.max_budget = float('inf')
#     except BudgetExceededError as e:
#         pass
#     except Exception as e:
#         pytest.fail(f"An error occured: {str(e)}")
