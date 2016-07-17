from fsttrpgcharloader.database import Actor, DBManager as ActorDBManager
from peewee import Model, SqliteDatabase, CharField, IntegerField, BooleanField, ForeignKeyField, DoubleField, \
    DoesNotExist

import aws

attributes_db = SqliteDatabase('attributes.db')


class BaseModel(Model):
    class Meta:
        database = attributes_db


class AttributeBlueprint(BaseModel):
    attribute_type = CharField()
    name = CharField(unique=True)
    category = CharField(null=True)
    cost = DoubleField()
    desc = CharField()

    @staticmethod
    def get_blueprint(attribute_type, name):
        bp = AttributeBlueprint.get(AttributeBlueprint.name == name,
                                    AttributeBlueprint.attribute_type == attribute_type)
        return bp

    @staticmethod
    def count_rows():
        return len(AttributeBlueprint.select())

    @staticmethod
    def add_or_modify(attribute_type, name, category, cost, desc):

        blueprint, created = AttributeBlueprint.get_or_create(attribute_type=attribute_type, name=name,
                                                              defaults={'category': category,
                                                                        'cost': cost,
                                                                        'desc': desc})
        if created:
            print('created new blueprint')
        else:
            blueprint.category = category
            blueprint.cost = cost
            blueprint.desc = desc
            blueprint.save()

    @staticmethod
    def get_all_of_type(type):
        return AttributeBlueprint.select().where(AttributeBlueprint.attribute_type == type)


class CareerPack(BaseModel):
    career_name = CharField()
    attribute_blueprint = ForeignKeyField(AttributeBlueprint, related_name='careers')

    @staticmethod
    def add(career_name, attr_type, attr_name):
        blueprint = AttributeBlueprint.get_blueprint(attribute_type=attr_type, name=attr_name)
        row, created = CareerPack.get_or_create(career_name=career_name, attribute_blueprint=blueprint)
        if created:
            print('created new skill to pack' + career_name)
        else:
            print('this skill is already part of pack: ' + career_name)

    @staticmethod
    def get_pack_names():
        names = []
        all = CareerPack.select()
        for row in all:
            if row.career_name in names:
                pass
            else:
                names.append(row.career_name)
        return names

    @staticmethod
    def get_pack_skills(pack_name):
        return CareerPack.select().where(CareerPack.career_name == pack_name)


class SkillBlueprint(BaseModel):
    blueprint = ForeignKeyField(AttributeBlueprint, related_name='skill_addons')
    chip_lvl_cost = IntegerField()
    chippable = BooleanField()
    diff = IntegerField()
    short = CharField()
    stat = CharField()

    @staticmethod
    def create_skill_blueprint(blueprint_name, chip_lvl_cost, chippable, diff, short, stat):
        blueprint = AttributeBlueprint.get_blueprint('skill', blueprint_name)
        skill_blueprint = SkillBlueprint(blueprint=blueprint, chip_lvl_cost=chip_lvl_cost, chippable=chippable,
                                         diff=diff, short=short, stat=stat)
        skill_blueprint.save()


class Skill(BaseModel):
    blueprint = ForeignKeyField(SkillBlueprint, related_name='effective_skills')
    actor = ForeignKeyField(Actor, related_name='actors')
    chipped = BooleanField(default=False)
    ip = IntegerField()
    lvl = IntegerField()
    carbon_lvl = IntegerField()
    field = CharField()

    @staticmethod
    def add_or_modify_skill(character_name, character_role, skill_name, chipped, ip, lvl, field):
        actor = Actor.add_or_get(name=character_name, role=character_role)
        blueprint = AttributeBlueprint.get_blueprint('skill', skill_name)
        skill, created = Skill.get_or_create(actor=actor, blueprint=blueprint,
                                             defaults={'chipped': chipped,
                                                       'ip': ip,
                                                       'lvl': lvl,
                                                       'carbon_lvl': lvl,
                                                       'field': field})
        if created:
            print('created new skill')
        else:
            print('modifying already existing skill')
            skill.chipped = chipped
            skill.ip = ip
            skill.lvl = lvl
            skill.field = field
            skill.blueprint = blueprint
            skill.save()


class Attribute(BaseModel):
    attribute_type = CharField()
    blueprint = ForeignKeyField(AttributeBlueprint, related_name='effective_attributes')
    actor = ForeignKeyField(Actor, related_name='character_attributes')
    lvl = IntegerField(null=True)
    field = CharField(null=True)

    @staticmethod
    def add_or_modify(attribute_type, blueprint_name, actor_name, actor_role, lvl, field):
        blueprint = AttributeBlueprint.get_blueprint(attribute_type=attribute_type, name=blueprint_name)
        act = Actor.add_or_get(role=actor_role, name=actor_name)
        attribute, created = Attribute.get_or_create(attribute_type=attribute_type, blueprint=blueprint, actor=act,
                                                     defaults={'lvl': lvl,
                                                               'field': field})
        if created:
            print('created new attribute')
        else:
            attribute.lvl = lvl
            attribute.field = field
        return attribute

    @staticmethod
    def get_attribute(attribute_type, actor_role, actor_name, blueprint_name):
        try:
            blueprint = AttributeBlueprint.get_blueprint(attribute_type=attribute_type, name=blueprint_name)
            act = Actor.add_or_get(role=actor_role, name=actor_name)
            attribute = Attribute.get(Attribute.actor == act, Attribute.blueprint == blueprint)
            return attribute
        except DoesNotExist as e:
            print(str(e))
            return None


class Perk(BaseModel):
    base_attribute = ForeignKeyField(Attribute, related_name='perks')
    target = ForeignKeyField(Actor, related_name='targets', null=True)

    @staticmethod
    def add_or_modify_perk(actor_role, actor_name, blueprint_name, lvl, field, target_role=None, target_name=None):
        attribute = Attribute.get_attribute('perk', actor_role=actor_role, actor_name=actor_name,
                                            blueprint_name=blueprint_name)
        target = None
        if attribute is None:
            attribute = Attribute.add_or_modify('perk', blueprint_name=blueprint_name, actor_name=actor_name,
                                                actor_role=actor_role,
                                                lvl=lvl, field=field)
        if target_name is not None:
            target = Actor.add_or_get(role=target_role, name=target_name)
        perk, created = Perk.get_or_create(base_attribute=attribute, target=target)
        if created:
            print('created new perk')
        else:
            pass


class Complication(BaseModel):
    base_attribute = ForeignKeyField(Attribute, related_name='complications')
    intensity = IntegerField()
    frequency = IntegerField()
    importance = IntegerField()

    def add_or_modify(self, actor_name, actor_role, blueprint_name, intensity, frequency, importance):

        attribute = Attribute.get_attribute(attribute_type='complication', actor_role=actor_role, actor_name=actor_name,
                                            blueprint_name=blueprint_name)
        if attribute is None:
            attribute = Attribute.add_or_modify('complication', blueprint_name=blueprint_name, actor_name=actor_name,
                                                actor_role=actor_role, lvl=0, field="")
        complication, created = Complication.get_or_create(base_attribute=attribute, defaults={'intensity': intensity,
                                                                                               'frequency': frequency,
                                                                                               'importance': importance})
        if created:
            print('created new complication')
        else:
            complication.intensity = intensity
            complication.frequency = frequency
            complication.importance = importance
            complication.save()


class DBManager(object):
    def __init__(self):
        self.actor_db_mgr = ActorDBManager()
        attributes_db.connect()
        attributes_db.create_tables([AttributeBlueprint, Skill, SkillBlueprint, Attribute, Perk, Complication,
                                     CareerPack], safe=True)

        self.attribute_blueprints = AttributeBlueprint()
        self.skill_blueprints = SkillBlueprint()
        self.attributes = Attribute()
        self.complications = Complication()
        self.perks = Perk()
        self.career_packs = CareerPack()

        if self.attribute_blueprints.count_rows() == 0:
            self.populate_attribute_blueprints()
        self.skills = Skill()

    def populate_attribute_blueprints(self):
        skills = aws.import_attributes_of_type('skill')
        perks = aws.import_attributes_of_type('perk')
        talents = aws.import_attributes_of_type('talent')
        complications = aws.import_attributes_of_type('complication')
        attributes = [skills, perks, talents, complications]
        # print(skills)

        for list_of_attributes in attributes:
            for a in list_of_attributes:
                self.attribute_blueprints.add_or_modify(attribute_type=a['type'], name=a['name'], category=a['category']
                                                        , cost=a['cost'], desc=a['desc'])
                if a['type'] == 'skill':
                    chippable = False
                    if a['chippable'] == 'yes':
                        chippable = True

                    self.skill_blueprints.create_skill_blueprint(blueprint_name=a['name'],
                                                                 chip_lvl_cost=a['chip_lvl_cost'],
                                                                 chippable=chippable, diff=a['diff'],
                                                                 short=a['short'], stat=a['stat'])

    def __del__(self):
        if attributes_db:
            attributes_db.close()


if __name__ == '__main__':
    db_mgr = DBManager()
