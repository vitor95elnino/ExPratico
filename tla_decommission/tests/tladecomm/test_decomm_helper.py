#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase
from tladecomm.decomm_helper import DecommHelper
from tladecomm.context import Context


class DecommHelperTest(TestCase):

    def setUp(self) -> None:
        self.context = Context()
        self.decom_helper = DecommHelper(self.context)

    def test___init__(self):
        self.skipTest('Constructor method')

    def test__initialize_services(self):
        self.skipTest('NOT TESTED YET')

    def test_dry_run(self):
        dry_run = self.decom_helper.dry_run()
        self.assertEqual(dry_run, '')

    def test_get_all_assets(self):
        self.skipTest('NOT TESTED YET')

    def test__initialize_osp10_providers(self):
        self.skipTest('NOT TESTED YET')

    def test__initialize_jenkins(self):
        self.skipTest('NOT TESTED YET')

    def test__initialize_service_scm(self):
        self.skipTest('NOT TESTED YET')

    def test_run(self):
        self.skipTest('NOT TESTED YET')

    def test__initialize_osp16_providers(self):
        providers = self.decom_helper.osp_services
        self.assertEqual(providers, '')
