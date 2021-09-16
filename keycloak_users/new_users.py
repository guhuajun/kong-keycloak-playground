import asyncio
import random
import sys

import names
from keycloak import KeycloakAdmin

# create apiadmin user and assign manage-users role
keycloak_admin = KeycloakAdmin(server_url='https://keycloak.apps.k3d.contoso.com/auth/',
                               username='apiadmin',
                               password='apiadmin',
                               realm_name='api.k3d.contoso.com',
                               verify='bundle.pem')


async def new_keycloak_user():
    name = names.get_full_name()

    first_name = name.split(' ')[0]
    last_name = name.split(' ')[1]

    alias = (first_name[0] + last_name).lower()
    user = {
        'email': f'{alias}@contoso.com',
        'username': f'{alias}',
        'enabled': True,
        'firstName': first_name,
        'lastName': last_name
    }

    sys.stdout.write('>')
    sys.stdout.flush()

    keycloak_admin.create_user(user)
    user_id = keycloak_admin.get_user_id(alias)
    keycloak_admin.set_user_password(user_id, 'abcd@123', False)


async def main():
    num_user = 2000
    await asyncio.gather(*[new_keycloak_user() for _ in range(num_user)])

if __name__ == '__main__':
    asyncio.run(main())
    print()
    print(f'Existing user number: {keycloak_admin.users_count()}')
