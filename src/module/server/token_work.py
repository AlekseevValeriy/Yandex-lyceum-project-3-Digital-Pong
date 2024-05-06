import secrets


class TokenCreate:
    @staticmethod
    def create(variant: str, exist_tokens: tuple[str] = []) -> str:
        while True:
            match variant:
                case 'user':
                    token = secrets.token_hex(8)
                case 'admin':
                    token = secrets.token_hex(32)
                case _:
                    token = secrets.token_hex(2)
            if token not in exist_tokens:
                break
        return token


class TokenVerification:
    @staticmethod
    def verification(token):
        match len(token):
            case 16:
                return 'user'
            case 64:
                return 'admin'
            case 4:
                return 'another'
        return 'unidentified'

if __name__ == '__main__':
    print(TokenCreate.create('admin'))
