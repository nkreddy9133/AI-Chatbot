from app.data.policies import SYNTHETIC_POLICIES

def get_policy_details(policy_id: str)->dict[str,object]:
    normalized_policy_id= policy_id.strip().upper()

    policy=SYNTHETIC_POLICIES.get(normalized_policy_id)

    if policy is None:
        return{
            "found": False,
            "policy_id": normalized_policy_id,
            "message": "No matching Policy was found."
        }

    return{
        "found": True,
        **policy
    }
   