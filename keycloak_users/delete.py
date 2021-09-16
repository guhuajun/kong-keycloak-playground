import names
from keycloak import KeycloakAdmin

if __name__ == '__main__':
    # create apiadmin user and assign manage-users role in Keycloak Realm
    keycloak_admin = KeycloakAdmin(server_url='https://keycloak.apps.k3d.contoso.com/auth/',
                                   username='apiadmin',
                                   password='apiadmin',
                                   realm_name='api.k3d.contoso.com',
                                   verify='bundle.pem')

    print(f'Existing user number: {keycloak_admin.users_count()}')

    users = keycloak_admin.get_users({})

    excluded_users = ['apiadmin', 'johnd']
    existing_users = []
    for x in users:
        try:
            if x['username'] not in excluded_users:
                existing_users.append(x['username'])
        except:
            print(x)

    for existing_user in existing_users:
        # print(f'Deleteing user {existing_user}')
        user_id = keycloak_admin.get_user_id(existing_user)
        keycloak_admin.delete_user(user_id)
