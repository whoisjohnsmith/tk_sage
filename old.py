'''
Simulator for TK sage damage.

- Missing actual min/max base damage values, bonus damage coefficients, actual crit chance calculation from crit rating, bonus damage calculation
- Damage of each ability is calculated over its cast/channeled duration, i.e. dots are applied instantly at start
- Does not take into consideration of potency/mental alacrity.
- Ignores alacrity.
- Does not check for ability cooldowns, up to you to right a viable template rotation.
'''

import random
import csv
import xml.etree.ElementTree as ET


class Ability(object):
    def __init__(self, ability_type, duration, min_base_damage, max_base_damage,
                 bonus_damage_coeff=1., ticks=1,
                 skill_crit_bonus=0., skill_surge_bonus=0.,
                 double_proc_chance=0., double_proc_damage_coeff=0.):
        
        self.type = ability_type # 'instant', 'cast', 'channeled', 'dot'
        self.min_base_damage = min_base_damage
        self.max_base_damage = max_base_damage
        self.duration = duration # in seconds
        self.bonus_damage_coeff = bonus_damage_coeff
        self.ticks = ticks
        self.skill_crit_bonus = skill_crit_bonus
        self.skill_surge_bonus = skill_surge_bonus
        self.double_proc_chance = double_proc_chance
        self.double_proc_damage_coeff = double_proc_damage_coeff # 0.-1., coeff of base damage

    def roll_damage(self, bonus_damage, base_crit, base_surge):
        damage = 0.
        crit = base_crit + self.skill_crit_bonus
        surge = base_surge + self.skill_surge_bonus
        for _ in range(self.ticks):
            base_damage_per_tick = random.randint(self.min_base_damage, self.max_base_damage) + self.bonus_damage_coeff * bonus_damage
            damage_per_tick = base_damage_per_tick
            crit_roll = random.random()*100
            if crit_roll <= crit:
                surge_damage = base_damage_per_tick * surge / 100.
                damage_per_tick += surge_damage
            if self.double_proc_chance > 0.:
                double_proc_roll = random.random()*100.
                if double_proc_roll <= self.double_proc_chance:
                    damage_per_tick += self.double_proc_damage_coeff/100. * base_damage_per_tick
            damage += damage_per_tick
        return damage, self.duration 


# also used for instants
class Casted_Ability(Ability):
    def __init__(self, duration, min_base_damage, max_base_damage,
                 bonus_damage_coeff=1., ticks=1,
                 skill_crit_bonus=0., skill_surge_bonus=0.,
                 double_proc_chance=0., double_proc_damage_coeff=0.):
        super(Casted_Ability, self).__init__('casted', duration, min_base_damage, max_base_damage, bonus_damage_coeff, ticks, skill_crit_bonus, skill_surge_bonus, double_proc_chance, double_proc_damage_coeff)


class Channeled_Ability(Ability):
    def __init__(self, duration, min_base_damage, max_base_damage,
                 bonus_damage_coeff=1., ticks=4,
                 skill_crit_bonus=0., skill_surge_bonus=0.,
                 double_proc_chance=0., double_proc_damage_coeff=0.):
        super(Channeled_Ability, self).__init__('channeled', duration, min_base_damage, max_base_damage, bonus_damage_coeff, ticks, skill_crit_bonus, skill_surge_bonus, double_proc_chance, double_proc_damage_coeff)


# initial damage + dot damage are calculated and applied as an instant
# duration is the cast time of the ability or gcd if instant cast
class DOT_Ability(Ability):
    def __init__(self, dot_ticks, dot_min_base_damage, dot_max_base_damage, dot_bonus_damage_coeff,
                 duration, min_base_damage, max_base_damage,
                 bonus_damage_coeff=1., ticks=4,
                 skill_crit_bonus=0., skill_surge_bonus=0.,
                 double_proc_chance=0., double_proc_damage_coeff=0.):
        self.dot_ticks = dot_ticks
        self.dot_min_base_damage = dot_min_base_damage # for the periodic, initial damage in parent
        self.dot_max_base_damage = dot_max_base_damage # for the periodic, initial damage in parent
        self.dot_bonus_damage_coeff = dot_bonus_damage_coeff
        super(DOT_Ability, self).__init__('dot', duration, min_base_damage, max_base_damage, bonus_damage_coeff, ticks, skill_crit_bonus, skill_surge_bonus, double_proc_chance, double_proc_damage_coeff)

    
    def roll_dot_tick_damage(self, bonus_damage, base_crit, base_surge):
        damage = 0.
        crit = base_crit + self.skill_crit_bonus
        surge = base_surge + self.skill_surge_bonus
        for _ in range(self.dot_ticks):
            base_damage_per_tick = random.randint(self.dot_min_base_damage, self.dot_max_base_damage) + self.dot_bonus_damage_coeff * bonus_damage
            damage_per_tick = base_damage_per_tick
            crit_roll = random.random()*100
            if crit_roll <= crit:
                surge_damage = base_damage_per_tick * surge / 100.
                damage_per_tick += surge_damage
            if self.double_proc_chance > 0.:
                double_proc_roll = random.random()*100.
                if double_proc_roll <= self.double_proc_chance:
                    damage_per_tick += self.double_proc_damage_coeff/100 * base_damage_per_tick
            damage += damage_per_tick
        return damage


    def roll_damage(self, bonus_damage, base_crit, base_surge):
        damage = 0.
        crit = base_crit #+ self.skill_crit_bonus
        surge = base_surge #+ self.skill_surge_bonus
        for _ in range(self.ticks):
            base_damage_per_tick = random.randint(self.min_base_damage, self.max_base_damage) + self.bonus_damage_coeff * bonus_damage
            damage_per_tick = base_damage_per_tick
            crit_roll = random.random()*100
            if crit_roll <= crit:
                surge_damage = base_damage_per_tick * surge / 100.
                damage_per_tick += surge_damage
            dot_damage = self.roll_dot_tick_damage(bonus_damage, base_crit, base_surge)
            damage += damage_per_tick + dot_damage
        return damage, self.duration  
    


class Ability_Disturbance(Casted_Ability):
    def __init__(self, duration=1.5, min_base_damage=1., max_base_damage=1.,
                 bonus_damage_coeff=1., ticks=1,
                 skill_crit_bonus=6., skill_surge_bonus=50.,
                 double_proc_chance=30., double_proc_damage_coeff=30.):
        super(Ability_Disturbance, self).__init__(duration, min_base_damage, max_base_damage,
                                bonus_damage_coeff, ticks,
                                skill_crit_bonus, skill_surge_bonus,
                                double_proc_chance, double_proc_damage_coeff)


class Ability_Wave(Casted_Ability):
    def __init__(self, duration=1.5, min_base_damage=1., max_base_damage=1.,
                 bonus_damage_coeff=1., ticks=1,
                 skill_crit_bonus=0., skill_surge_bonus=50.,
                 double_proc_chance=30., double_proc_damage_coeff=30.):
        super(Ability_Wave, self).__init__(duration, min_base_damage, max_base_damage,
                                bonus_damage_coeff, ticks,
                                skill_crit_bonus, skill_surge_bonus,
                                double_proc_chance, double_proc_damage_coeff)


class Ability_Project(Casted_Ability):
    def __init__(self, duration=1.5, min_base_damage=1., max_base_damage=1.,
                 bonus_damage_coeff=1., ticks=1,
                 skill_crit_bonus=0., skill_surge_bonus=0.,
                 double_proc_chance=50., double_proc_damage_coeff=30.):
        super(Ability_Project, self).__init__(duration, min_base_damage, max_base_damage,
                                bonus_damage_coeff, ticks,
                                skill_crit_bonus, skill_surge_bonus,
                                double_proc_chance, double_proc_damage_coeff)


class Ability_Turbulence(Casted_Ability):
    def __init__(self, duration=2.0, min_base_damage=1., max_base_damage=1.,
                 bonus_damage_coeff=1., ticks=1,
                 skill_crit_bonus=100., skill_surge_bonus=0.,
                 double_proc_chance=30., double_proc_damage_coeff=30.):
        super(Ability_Turbulence, self).__init__(duration, min_base_damage, max_base_damage,
                                bonus_damage_coeff, ticks,
                                skill_crit_bonus, skill_surge_bonus,
                                double_proc_chance, double_proc_damage_coeff)


class Ability_Tk_Throw(Channeled_Ability):
    def __init__(self, duration=3.0, min_base_damage=1., max_base_damage=1.,
                 bonus_damage_coeff=1., ticks=4,
                 skill_crit_bonus=6., skill_surge_bonus=0.,
                 double_proc_chance=0., double_proc_damage_coeff=0.):
        super(Ability_Tk_Throw, self).__init__(duration, min_base_damage, max_base_damage, bonus_damage_coeff, ticks, skill_crit_bonus, skill_surge_bonus, double_proc_chance, double_proc_damage_coeff)


class Ability_Weaken_Mind(DOT_Ability):
    def __init__(self, dot_ticks=6, dot_min_base_damage=1., dot_max_base_damage=1., dot_bonus_damage_coeff=1.,
                 duration=1.5, min_base_damage=0., max_base_damage=0.,
                 bonus_damage_coeff=1., ticks=1,
                 skill_crit_bonus=0., skill_surge_bonus=0.,
                 double_proc_chance=0., double_proc_damage_coeff=0.):
        super(Ability_Weaken_Mind, self).__init__(dot_ticks, dot_min_base_damage, dot_max_base_damage, dot_bonus_damage_coeff,
                                                  duration, min_base_damage, max_base_damage,
                                                  bonus_damage_coeff, ticks,
                                                  skill_crit_bonus, skill_surge_bonus,
                                                  double_proc_chance, double_proc_damage_coeff)
        
class Ability_Mind_Crush(DOT_Ability):
    def __init__(self, dot_ticks=6, dot_min_base_damage=1., dot_max_base_damage=1., dot_bonus_damage_coeff=1.,
                 duration=2.0, min_base_damage=0., max_base_damage=0.,
                 bonus_damage_coeff=1., ticks=1,
                 skill_crit_bonus=0., skill_surge_bonus=0.,
                 double_proc_chance=30., double_proc_damage_coeff=100.):
        super(Ability_Mind_Crush, self).__init__(dot_ticks, dot_min_base_damage, dot_max_base_damage, dot_bonus_damage_coeff,
                                                  duration, min_base_damage, max_base_damage,
                                                  bonus_damage_coeff, ticks,
                                                  skill_crit_bonus, skill_surge_bonus,
                                                  double_proc_chance, double_proc_damage_coeff)



class Sage2(object):
    def __init__(self, willpower, endurance, critical, power, force_power, surge, alacrity):
        self.willpower = willpower
        self.endurance = endurance
        self.critical = critical
        self.power = power
        self.force_power = force_power
        self.surge = surge
        self.alacrity = alacrity
        self.bonus_damage = self.return_bonus_damage()
        self.critical_change = self.return_critical_chance()
        
        self.a_disturbance = Ability_Disturbance()
        self.a_wave = Ability_Wave()
        self.a_project = Ability_Project()
        self.a_turbulence = Ability_Turbulence()
        self.a_tk_throw = Ability_Tk_Throw()
        self.a_weaken_mind = Ability_Weaken_Mind()
        self.a_mind_crush = Ability_Mind_Crush()
        
        self.a_dict = {'d':self.a_disturbance, 'w':self.a_wave, 'p':self.a_project, 't':self.a_turbulence, 'tkt':self.a_tk_throw, 'wm':self.a_weaken_mind, 'mc':self.a_mind_crush}

    def return_bonus_damage(self):
        return 1.
    
    def return_critical_chance(self):
        return 20.

    def run_rotation(self, template_rotation, times=1):
        clock = 0.
        total_damage = 0.
        for _ in range(times):
            for k in template_rotation:
                a = self.a_dict[k]
                damage, t = a.roll_damage(bonus_damage=self.bonus_damage, base_crit=self.critical_change, base_surge=self.surge)
                total_damage += damage
                clock += t
        
        print 'total damage:', total_damage
        print 'duration', clock
        print 'dps:', total_damage/clock
        

class Sage(object):
    def __init__(self, fname='sage.xml'):
        self.force_sheet = {}
        
        tree = ET.parse(fname)
        root = tree.getroot()
        e_force_sheet = root.find('force_sheet')
        
        for e in e_force_sheet:
            self.force_sheet[e.tag] = e.text


if __name__ == '__main__':
    sage = Sage()
    template_rotation = ['wm', 't', 'd', 'mc', 'tkt', 'w', 'd', 't', 'd', 'tkt', 'w', 'd', 'd']

#     sage = Sage2(1,1,1,1,1,1,1)
#     with open('old_template_rotation.csv', 'rb') as f:
#         template_rotation = [x.strip() for x in csv.reader(f, delimiter=',').next()]
#     print template_rotation
    sage.run_rotation(template_rotation, 1)
