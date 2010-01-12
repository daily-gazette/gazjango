from __future__ import division

from django.db import IntegrityError
from django.test import TestCase

from gazjango.ads.models import BannerAd
from gazjango.media.models import OutsideMedia, MediaBucket

import random

class SpaceCreationTestCase(TestCase):
    def setUp(self):
        self.bucket = MediaBucket.objects.create(slug='bucket')
        self.m = OutsideMedia.objects.create(bucket=self.bucket, slug='ad')
    
    def testDefaults(self):
        self.assertEqual(BannerAd.front.create(media=self.m).space, 'f')
        self.assertEqual(BannerAd.front.create(media=self.m, space='f').space, 'f')
        
        self.assertEqual(BannerAd.article_top.create(media=self.m).space, 't')
        self.assertEqual(BannerAd.article_top.create(media=self.m, space='t').space, 't')
        
        self.assertRaises(IntegrityError, lambda: BannerAd.objects.create(media=self.m))
    
    def testInvalidSpaces(self):
        self.assertRaises(ValueError, lambda: BannerAd.front.create(media=self.m, space='t'))
        self.assertRaises(ValueError, lambda: BannerAd.article_top.create(media=self.m, space='f'))
    

class BannerAdPriorityTestCase(TestCase):
    def setUp(self):
        self.bucket = MediaBucket.objects.create(slug='bucket')
        self.m = OutsideMedia.objects.create(bucket=self.bucket, slug='ad')
        self.make = lambda pri=1: BannerAd.front.create(media=self.m, priority=pri)
    
    def testEqualPriorities(self):
        for num in range(1, 5):
            self.make()
            self.priority_ratio_check(num_picks=500, delta=0.1)
    
    def testRandomPriorities(self):
        for num in range(1, 10):
            self.make(random.random() * 4)
            self.priority_ratio_check(num_picks=500, delta=0.1)
    
    def testZeroPriorityOnly(self):
        zero = self.make(0)
        for i in range(10):
            self.assertEqual(BannerAd.front.pick(), zero)
        
        # with two zero-priorities...
        self.make(0)
        self.priority_ratio_check(num_picks=100, delta=0.1)
    
    def testZerosAndNonzeros(self):
        zero = self.make(0)
        self.make(1)
        
        # shouldn't *ever* pick the zero if there's another
        self.priority_ratio_check(num_picks=30, delta=0)
        
        # regular priorities should still work
        self.make(2)
        picks = self.priority_ratio_check(num_picks=500, delta=0.1)
        self.assertEqual(picks[zero.pk], 0)
        
        # ...even if we have more than one zero
        zero_b = self.make(0)
        picks = self.priority_ratio_check(num_picks=500, delta=0.1)
        self.assertEqual(picks[zero.pk], 0)
        self.assertEqual(picks[zero_b.pk], 0)
    
    
    def pick_ratios(self, n=1000, base=BannerAd.front):
        counts = dict((ad.pk, 0) for ad in base.all())
        for i in range(n):
            counts[base.pick().pk] += 1
        return dict((pk, count / n) for pk, count in counts.items())
    
    def priority_ratios(self, base=BannerAd.front):
        ad_pks = base.all().values_list('pk', flat=True)
        total_priority = sum(ad.priority for ad in base.all())
        if total_priority > 0:
            return dict((pk, base.get(pk=pk).priority / total_priority) for pk in ad_pks)
        else:
            return dict((pk, 1/base.count()) for pk in ad_pks)
    
    def assert_values_in_delta(self, actual, expected, delta=0.04):
        for key in actual:
            self.assert_(abs(actual[key] - expected[key]) <= delta,
                        "value %3f, expected %3f" % (actual[key], expected[key]))
    
    def priority_ratio_check(self, num_picks=1000, delta=0.04, base=BannerAd.front):
        picks = self.pick_ratios(n=num_picks, base=base)
        self.assert_values_in_delta(picks, self.priority_ratios(base=base), delta)
        return picks
    
