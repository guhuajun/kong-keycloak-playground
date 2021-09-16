import os
import base64
import math
import random

from keycloak import KeycloakOpenID, KeycloakAdmin
from locust import HttpUser, LoadTestShape, TaskSet, constant, task


class UserTasks(TaskSet):

    # Get Token via pre-created usernames in Keycloak
    # users = ["aanderson", "abarnett", "adavis", "aforgey", "afortier", "afrazier", "ahamilton", "ahein", "ahuerta", "aparas",
    #          "apiadmin", "astewart", "avanorden", "avillasenor", "ayoung", "banderson", "bbaquet", "bboggs", "bbrumaghim", "bchan"]

    users = []
    username = ''
    token = ''
    keycloak_openid = None
    client_secret_key = os.environ.get('KEYCLOAK_LOCUST_CLIENT_SECRET_KEY', '360e445b-7e09-44c0-8184-5d788f076f5f')

    def login(self):
        password = 'YWJjZEAxMjM='
        self.username = random.choice(self.users)
        self.token = self.keycloak_openid.token(
            self.username, base64.b64decode(password))

    def on_start(self):
        # Configure client
        self.keycloak_openid = KeycloakOpenID(server_url="https://keycloak.apps.k3d.contoso.com/auth/",
                                              client_id="locust",
                                              realm_name="api.k3d.contoso.com",
                                              client_secret_key=self.client_secret_key,
                                              verify='bundle.pem')

        self.keycloak_admin = KeycloakAdmin(server_url='https://keycloak.apps.k3d.contoso.com/auth/',
                                            username='apiadmin',
                                            password='apiadmin',
                                            realm_name='api.k3d.contoso.com',
                                            verify='bundle.pem')

        self.users = [x['username'] for x in self.keycloak_admin.get_users()[0:20]]

        self.login()

    def on_stop(self):
        self.keycloak_openid.logout(self.token['refresh_token'])

    @task
    def get_root(self):
        headers = {'Authorization': 'Bearer {}'.format(
            self.token['access_token'])}
        response = self.client.get(
            "/date", headers=headers, verify='bundle.pem')

        if response.status_code == 401:
            self.login()

        if self.token['expires_in'] < 20:
            self.token = self.keycloak_openid.refresh_token(
                self.token['refresh_token'])


class WebsiteUser(HttpUser):
    try:
        wait_time = constant(os.environb.get('LOCUST_WAIT_TIME', 0.5))
    except:
        wait_time = constant(0.5)
    tasks = [UserTasks]


# class DoubleWave(LoadTestShape):
#     """
#     A shape to immitate some specific user behaviour. In this example, midday
#     and evening meal times. First peak of users appear at time_limit/3 and
#     second peak appears at 2*time_limit/3
#     Settings:
#         min_users -- minimum users
#         peak_one_users -- users in first peak
#         peak_two_users -- users in second peak
#         time_limit -- total length of test
#     """

#     min_users = 20
#     peak_one_users = 60
#     peak_two_users = 40
#     time_limit = 600

#     def tick(self):
#         run_time = round(self.get_run_time())

#         if run_time < self.time_limit:
#             user_count = (
#                 (self.peak_one_users - self.min_users)
#                 * math.e ** -(((run_time / (self.time_limit / 10 * 2 / 3)) - 5) ** 2)
#                 + (self.peak_two_users - self.min_users)
#                 * math.e ** -(((run_time / (self.time_limit / 10 * 2 / 3)) - 10) ** 2)
#                 + self.min_users
#             )
#             return (round(user_count), round(user_count))
#         else:
#             return None
