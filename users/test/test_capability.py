from . import TestBaseClass
from nose.tools import eq_
from users import User, Group, GroupToCapability, Capability


class TestCapability(TestBaseClass):

    def populate(self):
        with self.udb.atomic():
            cap1 = Capability.create(domain='res1', action=Capability.R)
            cap2 = Capability.create(domain='res2', action=Capability.U)
            grp1 = Group.create(name='grp2')
            grp2 = Group.create(name='grp1')
            usr = User.create(name='usr')
            grp1.capabilities.add(cap1)
            grp2.capabilities.add(cap2)
            usr.groups.add([grp1, grp2])
        return usr, [cap1, cap2]

    def test_capability_creation(self):
        Capability.create(domain='res', action=Capability.C)
        eq_(Capability.select().count(), 1)

    def test_assign_capability_to_group(self):
        cap = Capability.create(domain='res', action=Capability.D)
        anons = Group.create(name='anons')
        anons.capabilities.add(cap)
        anons.save()
        eq_(anons.capabilities.count(), 1)
        eq_(anons.capabilities.get(), cap)

    def test_get_capabilities_from_user(self):
        usr, caps = self.populate()
        userCapIds = [c.id for c in usr.capabilities]
        eq_(len(userCapIds), 2)
        eq_(set(userCapIds), set([c.id for c in caps]))

    def test_remove_capabilities(self):
        usr, caps = self.populate()
        Capability.delete().where(Capability.domain == caps[0].domain,
                                  Capability.action == caps[0].action).execute()
        eq_(usr.capabilities.count(), 1)
        eq_(usr.capabilities.get(), caps[1])
        eq_(GroupToCapability.select().count(), 1)

    def test_action_matching(self):
        cap = Capability.create(domain='s',
                                action=(Capability.C | Capability.R | Capability.U))
        self.assertTrue(cap.match_action(Capability.C))
        self.assertTrue(cap.match_action(Capability.R | Capability.R))
        self.assertFalse(cap.match_action(Capability.D))
        self.assertFalse(cap.match_action(Capability.R | Capability.D))
        self.assertFalse(cap.match_action(123123))

    def test_domain_matching_true(self):
        res = Capability.simToReg('volumes/*/attachments/*')
        cap = Capability.create(domain=res, action='21')
        self.assertTrue(cap.match_domain('volumes/j12j3213j/attachments/z7s71kj23'))
        self.assertTrue(cap.match_domain('/volumes/123nj12j3k/attachments/kj321k'))
        self.assertTrue(cap.match_domain('volumes/123nj12j3k/attachments/kj321k/'))

    def test_domain_matching_false(self):
        res = Capability.simToReg('volumes/*/attachments/*')
        cap = Capability.create(domain=res, action='21')
        self.assertFalse(cap.match_domain('volumes//attachments/z7s71kj23'))
        self.assertFalse(cap.match_domain('volumes/123123'))
        self.assertFalse(cap.match_domain('volumes/123123/attachments'))
        self.assertFalse(cap.match_domain('volumes/attachments/z7s71kj23'))
        self.assertFalse(cap.match_domain('volumes/j12j3213j/attachments'))
        self.assertFalse(cap.match_domain('volumes/j12j3213j/attachments/123123/name'))
        self.assertFalse(cap.match_domain('nothere/volumes/j12j3213j/attachments/123123/name'))

    def test_capability_matching(self):
        res = Capability.simToReg('/volumes/*/attachemnts/*')
        cap = Capability.create(domain=res,
                                action=Capability.R)
        cap.match('volumes/1/attachments/3', Capability.R)

    def test_simplified_to_reg_conversion(self):
        self.assertEqual(Capability.regToSim(Capability.simToReg('/volumes/*/attachments')), 'volumes/*/attachments')
        self.assertEqual(Capability.regToSim(Capability.simToReg('volumes/*/attachments/')), 'volumes/*/attachments')
        self.assertEqual(Capability.regToSim(Capability.simToReg('/*/')), '*')

    def test_user_can(self):
        cap1 = Capability.create(domain=Capability.simToReg('volumes/*'),
                                 action=Capability.C | Capability.R)
        cap2 = Capability.create(domain=Capability.simToReg('volumes/123'),
                                 action=Capability.U)
        grp1 = Group.create(name='grp2')
        grp2 = Group.create(name='grp1')
        usr = User.create(name='usr')
        grp1.capabilities.add(cap1)
        grp2.capabilities.add(cap2)
        usr.groups.add([grp1, grp2])
        self.assertTrue(usr.can('volumes/61273', action=Capability.C))
        self.assertTrue(usr.can('volumes/123', Capability.C | Capability.R))
        self.assertFalse(usr.can('volumes/82828', Capability.D))
        self.assertFalse(usr.can('volumes/123', Capability.D))

    def test_group_can(self):
        cap1 = Capability.create(domain=Capability.simToReg('volumes/*'),
                                 action=Capability.C | Capability.R)
        cap2 = Capability.create(domain=Capability.simToReg('users/123'),
                                 action=Capability.C | Capability.D)
        grp = Group.create(name='grp2')
        grp.capabilities.add([cap1, cap2])
        self.assertTrue(grp.can('volumes/123', Capability.C | Capability.R))
        self.assertFalse(grp.can('volumes/82828', Capability.D))
        self.assertTrue(grp.can('users/123', Capability.D))
        self.assertFalse(grp.can('users/123', Capability.U))
