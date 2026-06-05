class ValidationService:
    @staticmethod
    def valid_username(username):
        """Verifica os parâmetros exigidos para a validação do username."""
        tem_letra = any(c.isalpha() for c in username)
        tem_numero = any(c.isdigit() for c in username)
        tem_especial = any(not (c.isalnum() or c.isspace()) for c in username)
        tamanho = len(username) >= 5

        if not username.strip():
            return False, "O nome não pode estar vazio."
        if not tamanho:
            return False, "O nome deve ter pelo menos 5 caracteres."
        if tem_numero:
            return False, "O nome não deve conter números."
        if tem_especial:
            return False, "O nome não deve conter caracteres especiais."
        if not tem_letra:
            return False, "O nome deve conter letras."

        return True, None

    @staticmethod
    def valid_email(email, users):
        """Verifica os parâmetros exigidos para a validação do email."""
        tem_numero = any(c.isdigit() for c in email)
        tem_espaco = any(c.isspace() for c in email)
        tem_dominio = email.count("@") == 1
        tem_dominio_valido = email.endswith("@ufrpe.br")
        tamanho = len(email) > 9

        if not email.strip():
            return False, "O email não pode estar vazio."
        if tem_espaco:
            return False, "O email não deve conter espaços."
        if not tem_dominio:
            return False, "O email deve conter um '@'."
        if not tem_dominio_valido:
            return False, "Apenas emails '@ufrpe.br' são permitidos."
        if not tamanho:
            return False, "O email é muito curto."
        if tem_numero:
            return False, "O email não deve conter números."

        for u in users.values():
            if u["email"] == email:
                return False, "O email já existe."

        return True, None

    @staticmethod
    def valid_telephone_number(tellNum):
        """Verifica os parâmetros exigidos para a validação do número de contato."""
        tem_letra = any(c.isalpha() for c in tellNum)
        tem_numero = any(c.isdigit() for c in tellNum)
        tem_espaco = any(c.isspace() for c in tellNum)
        tem_especial = any(not (c.isalnum() or c.isspace()) for c in tellNum)
        tamanho = 10 < len(tellNum) <= 13

        if not tellNum.strip():
            return False, "O número é obrigatório."
        if tem_letra:
            return False, "O número não deve conter letras."
        if tem_espaco:
            return False, "O número não deve conter espaços."
        if tem_especial:
            return False, "O número não deve conter caracteres especiais."
        if not tem_numero:
            return False, "O número deve conter dígitos."
        if not tamanho:
            return False, "O número deve ter entre 11 e 13 dígitos."

        return True, None

    @staticmethod
    def valid_password(password):
        """Verifica os parâmetros exigidos para a validação da senha."""
        tem_letra = any(c.isalpha() for c in password)
        tem_numero = any(c.isdigit() for c in password)
        tem_especial = any(not (c.isalnum() or c.isspace()) for c in password)
        tamanho = len(password) >= 8
        tem_maiuscula = any(c.isupper() for c in password)
        tem_minuscula = any(c.islower() for c in password)

        if not tem_letra:
            return False, "A senha deve conter pelo menos uma letra."
        if not tem_numero:
            return False, "A senha deve conter pelo menos um número."
        if not tem_especial:
            return False, "A senha deve conter pelo menos um caractere especial."
        if not tamanho:
            return False, "A senha deve ter pelo menos 8 caracteres."
        if not tem_maiuscula:
            return False, "A senha deve conter pelo menos um caractere em maiúscula."
        if not tem_minuscula:
            return False, "A senha deve conter pelo menos um caractere em minúscula."

        return True, None
