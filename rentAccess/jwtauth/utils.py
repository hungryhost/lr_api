

def username_generate_from_email(email, user_id):
    name, _, _ = email.partition("@")
    username = name + "_" + str(user_id)
    return username
