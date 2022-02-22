import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
from pprint import pprint
# import json
from urllib.parse import urlencode
from copy import deepcopy

class Instagram2Spider(scrapy.Spider):
    name = 'instagram2'
    start_urls = ['https://www.instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = 'Cresset_El'
    with open('lesson8.txt') as f:
        inst_password = f.read()
    # user_pars = 'mongolschuudan'
    user_pars = ['engineer_history.ru', 'mongolschuudan']
    api_url = 'https://i.instagram.com/api/v1/friendships/'


    def parse(self, response: HtmlResponse):
        csrf = self.get_csrf_token(response.text)
        yield scrapy.FormRequest(self.inst_login_link, method='POST',
                                 callback=self.login,
                                 formdata={'username': self.inst_login, 'enc_password': self.inst_password},
                                 headers={'x-csrftoken': csrf})


    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data.get('authenticated'):
            for elem in self.user_pars:
                yield response.follow(f'/{elem}/', callback=self.user_data_parse,
                                      cb_kwargs={'username': elem})


    def user_data_parse(self, response: HtmlResponse, username):
        # with open('res11.txt', 'w') as f:
        #     f.write(response.text)
        user_id = self.get_user_id(response.text)
        variables_er = {'count': 12, 'max_id': 12}
        variables_ing = {'count': 12, 'max_id': 12}
        followers_url = f'{self.api_url}{user_id}/followers/?&{urlencode(variables_er)}&search_surface=follow_list_pag'
        yield response.follow(followers_url,
                              callback=self.user_followers_parse,
                              cb_kwargs={'username': username, 'user_id': user_id, 'variables_er': deepcopy(variables_er)}
                              )
        following_url = f'{self.api_url}{user_id}/following/?&{urlencode(variables_ing)}'
        # following_url = f'{self.api_url}{user_id}/following/?count=12&max_id=1008&search_surface=follow_list_pag'
        yield response.follow(following_url,
                              callback=self.user_following_parse,
                              cb_kwargs={'username': username, 'user_id': user_id, 'variables_ing': deepcopy(variables_ing)}
                              )


    def user_followers_parse(self, response: HtmlResponse, username, user_id, variables_er):
        j_data = response.json()
        # with open('followers.txt', 'w') as f:
        #     f.write(response.text)
        if j_data.get('next_max_id'):
            variables_er['max_id'] += 12
            # followers_url = f'{self.api_url}friendships/{user_id}/following/?&{urlencode(variables_er)}&search_surface=follow_list_pag'
            followers_url = f'{self.api_url}{user_id}/followers/?&{urlencode(variables_er)}&search_surface=follow_list_pag'
            yield response.follow(followers_url,
                                  callback=self.user_followers_parse,
                                  cb_kwargs={'username': username, 'user_id': user_id, 'variables_er': deepcopy(variables_er)}
                                  )
        followers = j_data.get('users')
        for follower in followers:
            item = InstaparserItem(
                target_username=username,
                target_user_id=user_id,
                photo=follower.get('profile_pic_url'),
                username=follower.get('username'),
                user_id=follower.get('pk'),
                user_data=follower,
                follower=True
            )
            yield item

    def user_following_parse(self, response: HtmlResponse, username, user_id, variables_ing):
        j_data = response.json()
        # with open('followers.txt', 'w') as f:
        #     f.write(response.text)
        if j_data.get('next_max_id'):
            variables_ing['max_id'] += 12
            # followers_url = f'{self.api_url}friendships/{user_id}/following/?&{urlencode(variables_er)}&search_surface=follow_list_pag'
            following_url = f'{self.api_url}{user_id}/following/?&{urlencode(variables_ing)}'
            yield response.follow(following_url,
                                  callback=self.user_following_parse,
                                  cb_kwargs={'username': username, 'user_id': user_id, 'variables_ing': deepcopy(variables_ing)}
                                  )
        followings = j_data.get('users')
        for following in followings:
            item = InstaparserItem(
                target_username=username,
                target_user_id=user_id,
                photo=following.get('profile_pic_url'),
                username=following.get('username'),
                user_id=following.get('pk'),
                user_data=following,
                following=True
            )
            yield item

    def get_csrf_token(self, text):
        token = ''
        n = text.find('csrf_token')
        if n != -1:
            while text[n + 13] != '"':
                token += text[n + 13]
                n += 1
        return token

    def get_user_id(self, text):
        user_id = ''
        n = text.find('owner')
        if n != -1:
            while text[n + 14] != '"':
                user_id += text[n + 14]
                n += 1
        return user_id
