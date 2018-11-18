# Create your tests here.

from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase

import logging

from openbook_common.tests.helpers import make_authentication_headers_for_user, make_fake_post_text, \
    make_fake_post_comment_text, make_user, make_circle
from openbook_posts.models import Post, PostComment

logger = logging.getLogger(__name__)
fake = Faker()


class PostItemAPITests(APITestCase):
    """
    PostItemAPI
    """

    def test_can_delete_own_post(self):
        """
        should be able to delete own post and return 200
        """
        user = make_user()
        headers = make_authentication_headers_for_user(user)
        post = user.create_post(text=make_fake_post_text())

        url = self._get_url(post)

        response = self.client.delete(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Post.objects.filter(pk=post.pk).count() == 0)

    def test_cannot_delete_foreign_post(self):
        """
        should not be able to delete a foreign post and return 400
        """
        user = make_user()
        headers = make_authentication_headers_for_user(user)

        foreign_user = make_user()
        post = foreign_user.create_post(text=make_fake_post_text())

        url = self._get_url(post)

        response = self.client.delete(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Post.objects.filter(pk=post.pk).count() == 1)

    def _get_url(self, post):
        return reverse('post', kwargs={
            'post_id': post.pk
        })


class PostCommentsAPITests(APITestCase):
    """
    PostCommentsAPI
    """

    def test_can_comment_in_own_post(self):
        """
         should be able to comment in own post and return 201
         """
        user = make_user()
        headers = make_authentication_headers_for_user(user)
        post = user.create_post(text=make_fake_post_text())

        post_comment_text = make_fake_post_comment_text()

        data = self._get_create_post_comment_request_data(post_comment_text)

        url = self._get_url(post)
        response = self.client.put(url, data, **headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PostComment.objects.filter(post_id=post.pk, text=post_comment_text).count() == 1)

    def test_cannot_comment_in_foreign_post(self):
        """
         should not be able to comment in a foreign encircled post and return 400
         """
        user = make_user()
        headers = make_authentication_headers_for_user(user)

        foreign_user = make_user()
        circle = make_circle(creator=foreign_user)
        post = foreign_user.create_post(text=make_fake_post_text(), circle=circle)

        post_comment_text = make_fake_post_comment_text()

        data = self._get_create_post_comment_request_data(post_comment_text)

        url = self._get_url(post)
        response = self.client.put(url, data, **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(PostComment.objects.filter(post_id=post.pk, text=post_comment_text).count() == 0)

    def test_can_comment_in_connected_user_public_post(self):
        """
         should be able to comment in the public post of a connected user post and return 201
         """
        user = make_user()
        headers = make_authentication_headers_for_user(user)

        user_to_connect = make_user()

        user.connect_with_user_with_id(user_to_connect.pk)

        connected_user_post = user_to_connect.create_post(text=make_fake_post_text())

        post_comment_text = make_fake_post_comment_text()

        data = self._get_create_post_comment_request_data(post_comment_text)

        url = self._get_url(connected_user_post)
        response = self.client.put(url, data, **headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PostComment.objects.filter(post_id=connected_user_post.pk, text=post_comment_text).count() == 1)

    def test_can_comment_in_connected_user_encircled_post_part_of(self):
        """
          should be able to comment in the encircled post of a connected user which the user is part of and return 201
        """
        user = make_user()
        headers = make_authentication_headers_for_user(user)

        user_to_connect = make_user()
        circle = make_circle(creator=user_to_connect)

        user.connect_with_user_with_id(user_to_connect.pk)
        user_to_connect.confirm_connection_with_user_with_id(user.pk, circle_id=circle.pk)

        connected_user_post = user_to_connect.create_post(text=make_fake_post_text(), circle=circle)

        post_comment_text = make_fake_post_comment_text()

        data = self._get_create_post_comment_request_data(post_comment_text)

        url = self._get_url(connected_user_post)
        response = self.client.put(url, data, **headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PostComment.objects.filter(post_id=connected_user_post.pk, text=post_comment_text).count() == 1)

    def test_cannot_comment_in_connected_user_encircled_post_not_part_of(self):
        """
             should NOT be able to comment in the encircled post of a connected user which the user is NOT part of and return 400
        """
        user = make_user()
        headers = make_authentication_headers_for_user(user)

        user_to_connect = make_user()
        circle = make_circle(creator=user_to_connect)

        user.connect_with_user_with_id(user_to_connect.pk)
        # Note there is no confirmation of the connection on the other side

        connected_user_post = user_to_connect.create_post(text=make_fake_post_text(), circle=circle)

        post_comment_text = make_fake_post_comment_text()

        data = self._get_create_post_comment_request_data(post_comment_text)

        url = self._get_url(connected_user_post)
        response = self.client.put(url, data, **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue(PostComment.objects.filter(post_id=connected_user_post.pk, text=post_comment_text).count() == 0)

    def test_can_comment_in_user_public_post(self):
        """
          should be able to comment in the public post of any user and return 201
        """
        user = make_user()
        headers = make_authentication_headers_for_user(user)

        foreign_user = make_user()

        foreign_user_post = foreign_user.create_post(text=make_fake_post_text(), circle_id=foreign_user.world_circle_id)

        post_comment_text = make_fake_post_comment_text()

        data = self._get_create_post_comment_request_data(post_comment_text)

        url = self._get_url(foreign_user_post)
        response = self.client.put(url, data, **headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PostComment.objects.filter(post_id=foreign_user_post.pk, text=post_comment_text).count() == 1)

    def test_cannot_comment_in_followed_user_encircled_post(self):
        """
          should be able to comment in the encircled post of a followed user return 400
        """
        user = make_user()
        headers = make_authentication_headers_for_user(user)

        user_to_follow = make_user()
        circle = make_circle(creator=user_to_follow)

        user.follow_user_with_id(user_to_follow.pk)

        followed_user_post = user_to_follow.create_post(text=make_fake_post_text(), circle=circle)

        post_comment_text = make_fake_post_comment_text()

        data = self._get_create_post_comment_request_data(post_comment_text)

        url = self._get_url(followed_user_post)
        response = self.client.put(url, data, **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(PostComment.objects.filter(post_id=followed_user_post.pk, text=post_comment_text).count() == 0)

    def _get_create_post_comment_request_data(self, post_comment_text):
        return {
            'text': post_comment_text
        }

    def _get_url(self, post):
        return reverse('post-comments', kwargs={
            'post_id': post.pk,
        })


class PostCommentItemAPITests(APITestCase):
    """
    PostCommentItemAPI
    """

    def test_can_delete_foreign_comment_in_own_post(self):
        """
          should be able to delete a foreign comment in own post and return 200
        """
        user = make_user()

        commenter = make_user()

        post = user.create_post(text=make_fake_post_text(), circle_id=user.world_circle_id)

        post_comment_text = make_fake_post_comment_text()

        post_comment = commenter.comment_post_with_id(post.pk, text=post_comment_text)

        url = self._get_url(post_comment=post_comment, post=post)

        headers = make_authentication_headers_for_user(user)
        response = self.client.delete(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(PostComment.objects.filter(id=post_comment.pk).count() == 0)

    def test_can_delete_own_comment_in_foreign_public_post(self):
        """
          should be able to delete own comment in foreign public post and return 200
        """
        user = make_user()

        foreign_user = make_user()

        post = foreign_user.create_public_post(text=make_fake_post_text())

        post_comment_text = make_fake_post_comment_text()

        post_comment = user.comment_post_with_id(post.pk, text=post_comment_text)

        url = self._get_url(post_comment=post_comment, post=post)

        headers = make_authentication_headers_for_user(user)
        response = self.client.delete(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(PostComment.objects.filter(id=post_comment.pk).count() == 0)

    def test_cannot_delete_foreign_comment_in_foreign_public_post(self):
        """
          should NOT be able to delete foreign comment in foreign public post and return 400
        """
        user = make_user()

        foreign_user = make_user()

        post = foreign_user.create_public_post(text=make_fake_post_text())

        post_comment_text = make_fake_post_comment_text()

        post_comment = foreign_user.comment_post_with_id(post.pk, text=post_comment_text)

        url = self._get_url(post_comment=post_comment, post=post)

        headers = make_authentication_headers_for_user(user)
        response = self.client.delete(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(PostComment.objects.filter(id=post_comment.pk).count() == 1)

    def test_can_delete_own_comment_in_connected_user_public_post(self):
        """
          should be able to delete own comment in a connected user public post and return 200
        """
        user = make_user()

        user_to_connect = make_user()

        user.connect_with_user_with_id(user_to_connect.pk)
        user_to_connect.confirm_connection_with_user_with_id(user.pk)

        post = user_to_connect.create_public_post(text=make_fake_post_text())

        post_comment_text = make_fake_post_comment_text()

        post_comment = user.comment_post_with_id(post.pk, text=post_comment_text)

        url = self._get_url(post_comment=post_comment, post=post)

        headers = make_authentication_headers_for_user(user)
        response = self.client.delete(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(PostComment.objects.filter(id=post_comment.pk).count() == 0)

    def test_cannot_delete_foreign_comment_in_connected_user_public_post(self):
        """
          should not be able to delete foreign comment in a connected user public post and return 400
        """
        user = make_user()

        user_to_connect = make_user()

        user.connect_with_user_with_id(user_to_connect.pk)
        user_to_connect.confirm_connection_with_user_with_id(user.pk)

        foreign_user = make_user()

        post = user_to_connect.create_public_post(text=make_fake_post_text())

        post_comment_text = make_fake_post_comment_text()

        post_comment = foreign_user.comment_post_with_id(post.pk, text=post_comment_text)

        url = self._get_url(post_comment=post_comment, post=post)

        headers = make_authentication_headers_for_user(user)
        response = self.client.delete(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(PostComment.objects.filter(id=post_comment.pk).count() == 1)

    def test_can_delete_own_comment_in_connected_user_encircled_post_part_of(self):
        """
           should be able to delete own comment in a connected user encircled post it's part of and return 200
         """
        user = make_user()

        user_to_connect = make_user()
        circle = make_circle(creator=user_to_connect)

        user.connect_with_user_with_id(user_to_connect.pk)
        user_to_connect.confirm_connection_with_user_with_id(user.pk, circle_id=circle.pk)

        post = user_to_connect.create_post(text=make_fake_post_text(), circle_id=circle.pk)

        post_comment_text = make_fake_post_comment_text()

        post_comment = user.comment_post_with_id(post.pk, text=post_comment_text)

        url = self._get_url(post_comment=post_comment, post=post)

        headers = make_authentication_headers_for_user(user)
        response = self.client.delete(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(PostComment.objects.filter(id=post_comment.pk).count() == 0)

    def test_cannot_delete_foreign_comment_in_connected_user_encircled_post_part_of(self):
        """
           should NOT be able to delete foreign comment in a connected user encircled post it's part of and return 400
         """
        user = make_user()

        user_to_connect = make_user()
        circle = make_circle(creator=user_to_connect)

        user.connect_with_user_with_id(user_to_connect.pk)
        user_to_connect.confirm_connection_with_user_with_id(user.pk, circle_id=circle.pk)

        foreign_user = make_user()
        foreign_user.connect_with_user_with_id(user_to_connect.pk)
        user_to_connect.confirm_connection_with_user_with_id(foreign_user.pk, circle_id=circle.pk)

        post = user_to_connect.create_post(text=make_fake_post_text(), circle_id=circle.pk)

        post_comment_text = make_fake_post_comment_text()

        post_comment = foreign_user.comment_post_with_id(post.pk, text=post_comment_text)

        url = self._get_url(post_comment=post_comment, post=post)

        headers = make_authentication_headers_for_user(user)
        response = self.client.delete(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(PostComment.objects.filter(id=post_comment.pk).count() == 1)

    def test_cannot_delete_foreign_comment_in_connected_user_encircled_post_not_part_of(self):
        """
           should NOT be able to delete foreign comment in a connected user encircled post NOT part of and return 400
         """
        user = make_user()

        user_to_connect = make_user()
        circle = make_circle(creator=user_to_connect)

        foreign_user = make_user()
        foreign_user.connect_with_user_with_id(user_to_connect.pk)
        user_to_connect.confirm_connection_with_user_with_id(foreign_user.pk, circle_id=circle.pk)

        post = user_to_connect.create_post(text=make_fake_post_text(), circle_id=circle.pk)

        post_comment_text = make_fake_post_comment_text()

        post_comment = foreign_user.comment_post_with_id(post.pk, text=post_comment_text)

        url = self._get_url(post_comment=post_comment, post=post)

        headers = make_authentication_headers_for_user(user)
        response = self.client.delete(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(PostComment.objects.filter(id=post_comment.pk).count() == 1)

    def test_can_delete_own_comment_in_followed_user_public_post(self):
        """
           should be able to delete own comment in a followed user public post and return 200
         """
        user = make_user()

        user_to_follow = make_user()

        user.follow_user_with_id(user_to_follow.pk)

        post = user_to_follow.create_public_post(text=make_fake_post_text())

        post_comment_text = make_fake_post_comment_text()

        post_comment = user.comment_post_with_id(post.pk, text=post_comment_text)

        url = self._get_url(post_comment=post_comment, post=post)

        headers = make_authentication_headers_for_user(user)
        response = self.client.delete(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(PostComment.objects.filter(id=post_comment.pk).count() == 0)

    def test_cannot_delete_foreign_comment_in_followed_user_public_post(self):
        """
           should not be able to delete foreign comment in a followed user public post and return 400
         """
        user = make_user()

        user_to_follow = make_user()

        user.follow_user_with_id(user_to_follow.pk)

        foreign_user = make_user()

        post = user_to_follow.create_public_post(text=make_fake_post_text())

        post_comment_text = make_fake_post_comment_text()

        post_comment = foreign_user.comment_post_with_id(post.pk, text=post_comment_text)

        url = self._get_url(post_comment=post_comment, post=post)

        headers = make_authentication_headers_for_user(user)
        response = self.client.delete(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(PostComment.objects.filter(id=post_comment.pk).count() == 1)

    def test_cannot_delete_foreign_comment_in_folowed_user_encircled_post(self):
        """
             should not be able to delete foreign comment in a followed user encircled post and return 400
        """
        user = make_user()

        user_to_follow = make_user()
        circle = make_circle(creator=user_to_follow)

        user.follow_user_with_id(user_to_follow.pk)

        foreign_user = make_user()
        foreign_user.connect_with_user_with_id(user_to_follow.pk)
        user_to_follow.confirm_connection_with_user_with_id(foreign_user, circle_id=circle.pk)

        post = user_to_follow.create_post(text=make_fake_post_text(), circle_id=circle.pk)

        post_comment_text = make_fake_post_comment_text()

        post_comment = foreign_user.comment_post_with_id(post.pk, text=post_comment_text)

        url = self._get_url(post_comment=post_comment, post=post)

        headers = make_authentication_headers_for_user(user)
        response = self.client.delete(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(PostComment.objects.filter(id=post_comment.pk).count() == 1)

    def _get_url(self, post, post_comment):
        return reverse('post-comment', kwargs={
            'post_id': post.pk,
            'post_comment_id': post_comment.pk
        })