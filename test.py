import jwt

token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2Nzg4MTYwNjIsImlhdCI6MTY3ODgxMjQ2Miwic3ViIjoiMjExYzBlMGYtNjIzYy00NWU1LWFiOGYtMWZhZTNmMTNkMGRiIn0.NBw8_Rr_e2q3NuBbPiOm9leHOuD1v-e7-022T4OCmpM'

try:
    # Decode the token using the PyJWT library and the secret key
    decoded = jwt.decode(token, 'atyponisthebest', algorithms=['HS256'])
    print(decoded)
except jwt.exceptions.InvalidTokenError:
    print('Invalid token')
