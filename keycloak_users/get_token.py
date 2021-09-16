from keycloak import KeycloakAdmin

if __name__ == '__main__':
    # create apiadmin user and assign manage-users role in Keycloak Realm
    keycloak_admin = KeycloakAdmin(server_url='https://keycloak.apps.k3d.contoso.com/auth/',
                                   username='apiadmin',
                                   password='apiadmin',
                                   realm_name='api.k3d.contoso.com',
                                   verify='bundle.pem')

    keycloak_admin.get_token()