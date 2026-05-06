def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False
    
    specials = set('!@#$%^&*(),.?":{}|<>')
    has_letter = False
    has_special = False
    has_number = False
    has_upper = False
    for c in password:
        if c.isdigit():
            has_number = True
        if c.isupper():
            has_upper = True
        if c.isalpha():
            has_letter = True
        if c in specials:
            has_special = True

        if has_special and has_number and has_letter and has_upper:
            return True
        
    return False