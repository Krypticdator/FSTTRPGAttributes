from traits.api import HasTraits, Instance, String, Button
from traitsui.api import View, HGroup, Item, VGroup, Tabbed, TextEditor

from fsttrpgattributes.models import AttributeLists
from models import TalentList, PerkList, SkillList, ComplicationList, Skill

SKILL_LIST = AttributeLists('skill')


class SkillWithDescBox(Skill):
    desc = String(editor=TextEditor(multi_line=True))

    def _name_changed(self):
        self.desc = str(SKILL_LIST.descriptions[self.name])

    def __init__(self):
        pass

    view = View(
        HGroup(
            Item('name'),
            Item('field'),
            Item('lvl'),
            Item('desc', style='custom')
        )
    )


class SkillTest(HasTraits):
    skill1 = Instance(SkillWithDescBox, ())
    skill2 = Instance(SkillWithDescBox, ())

    view = View(
        Item('skill1', style='custom'),
        Item('skill2', style='custom')
    )


class AllAttributeListsView(HasTraits):
    skills = Instance(SkillList, ())
    complications = Instance(ComplicationList, ())
    perks = Instance(PerkList, ())
    talents = Instance(TalentList, ())
    # label = 'Personnel profile', show_border = True

    view = View(
        VGroup(
            Item('skills', style='custom', show_label=False),
            Item('complications', style='custom', show_label=False),
            Item('perks', style='custom', show_label=False),
            Item('talents', style='custom', show_label=False)
        )
    )


class AllAttributeListsTabbedView(AllAttributeListsView):
    save = Button()  # TODO delete me
    load = Button()  # TODO delete me

    def _save_fired(self):
        self.skills.save('Testi', 'NPC')
        self.complications.save('Testi', 'NPC')
        self.perks.save('Testi', 'NPC')
        self.talents.save('Testi', 'NPC')

    def _load_fired(self):
        self.complications.load('Testi', 'NPC')
        self.skills.load('Testi', 'NPC')

    view = View(
        Tabbed(
            Item('skills', style='custom', show_label=False),
            Item('complications', style='custom', show_label=False),
            Item('perks', style='custom', show_label=False),
            Item('talents', style='custom', show_label=False)
        ),
        Item('save', show_label=False),
        Item('load', show_label=False)
    )


if __name__ == '__main__':
    all_atr_view = AllAttributeListsTabbedView()
    all_atr_view.configure_traits()
    # db_mgr = DBManager()
    # attributes = db_mgr.perks.get_perks_of_actor('NPC', 'Testi')
    # db_mgr.skills.load_skills_of('NPC', 'Testi')