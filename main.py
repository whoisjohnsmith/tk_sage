import xml.etree.ElementTree as ET
import random
import ast


def make_dict_from_child_elements(root, child_tag):
    ret = {}
    child = root.find(child_tag)
    for e in child:
        try:
            ret[e.tag] = float(e.text)
        except ValueError:
            ret[e.tag] = e.text
    return ret

class Sage(object):
    def __init__(self, fname='sage.xml'):        
        tree = ET.parse(fname)
        self.root = tree.getroot()
        
        self.base_stats = make_dict_from_child_elements(self.root, 'base_stats')
        self.force_sheet = make_dict_from_child_elements(self.root, 'force_sheet')
#         if self.root.find('base_stats').attrib['calculate_metastats'] == 'yes':
#             pass
#         else:
#             self.force_sheet = make_dict_from_child_elements(self.root, 'force_sheet')
        
        self.abilities = {'disturbance':Disturbance(),
                          'project':Project(),
                          'turbulence':Turbulence(),
                          'tk_wave':Telekinetic_Wave(),
                          'tk_throw':Telekinetic_Throw(),
                          'weaken_mind':Weaken_Mind(),
                          'mind_crush':Mind_Crush()}


    def force_sheet_from_base_stats(self):
        force_sheet = {}
        force_sheet['bonus_damage'] = 0.
        force_sheet['bonus_healing'] = 0.
        force_sheet['accuracy'] = self.__return_accuracy()
        force_sheet['critical_chance'] = 0.0
        force_sheet['critical_multiplier'] = 0.0
        force_sheet['force_regen_rate'] = 0.0
        force_sheet['activation_speed'] = 0.0        
        return force_sheet


    def return_bonus_damage(self):
        return 0.0
    
    def __return_accuracy(self):
        #faccuracy = 0.3*(1-(1-1/30).^(accuracyRating/55/1.2)) + innerStrengthAcc + 0.01
        inner_strength = int(self.root.find('skills').find('inner_strength').text) * 0.01
        companion_bonus = float(self.root.find('companion_bonuses').find('accuracy').text) / 100.
        accuracy = 0.3 * (1. - (1. - 1/30)**(self.base_stats['accuracy_rating']/55./1.2)) + inner_strength + companion_bonus
        return accuracy


class Mob(object):
    def __init__(self):
        print 'mob class not implemented yet'


class Ability(object):
    def __init__(self, fname):
        tree = ET.parse(fname)
        root = tree.getroot()
        
        self.description = make_dict_from_child_elements(root, 'description')
        self.skills_affecting = make_dict_from_child_elements(root, 'skills_affecting')


    def is_critical_hit(self, critical_chance):
        critical_roll = random.random()*100
        critical_hit = critical_roll <= critical_chance
        return critical_hit
        
    def return_critical_damage(self, damage, critical_mutliplier):
        critical_damage = damage * critical_mutliplier / 100.
        return critical_damage
    
    def is_double_proc(self, double_proc_chance):
        double_proc_roll = random.random()*100
        double_proc = double_proc_roll <= double_proc_chance
        return double_proc

    def return_double_proc_damage(self, damage, double_proc_mutliplier):
        double_proc_damage = damage * double_proc_mutliplier / 100.
        return double_proc_damage


class Damage_Profile(object):
    '''obsolete
    '''
    def __init__(self, ability_name=None, clock_step=None, total_damage=None, base_damage=None, critical_hit=None, critical_damage=None, double_proc_hit=None, double_proc_damage=None):
        self.ability_name = ability_name
        self.clock_step = clock_step
        self.total_damage = total_damage
        self.base_damage = base_damage
        self.critical_hit = critical_hit
        self.critical_damage = critical_damage
        self.double_proc_hit = double_proc_hit
        self.double_proc_damage = double_proc_damage


class Damage_Results(object):
    def __init__(self, ability_name, clock_step, total_damage, number_of_ticks, number_of_critical_ticks, main_attack_critical=None, double_proc=None, double_proc_damage=None, double_proc_critical=None, mind_crush_num_extra_ticks=None):
        self.ability_name = ability_name
        self.clock_step = clock_step
        self.total_damage = total_damage
        self.number_of_ticks = number_of_ticks
        self.number_of_critical_ticks = number_of_critical_ticks
        
        self.main_attack_critical = main_attack_critical
        
        self.double_proc = double_proc
        self.double_proc_damage = double_proc_damage
        self.double_proc_critical = double_proc_critical
        
        self.mind_crush_num_extra_ticks = mind_crush_num_extra_ticks


class Disturbance(Ability):
    def __init__(self, fname='disturbance.xml'):
        super(Disturbance, self).__init__(fname)

    def damage(self, sage, mob):
        '''
        Not sure when damage_increase is applied, have it before crit at the moment
        '''
        bonus_damage = sage.force_sheet['bonus_damage']
        accuracy = sage.force_sheet['accuracy']
        critical_chance = sage.force_sheet['critical_chance']
        critical_multiplier = sage.force_sheet['critical_multiplier']
        activation_speed = sage.force_sheet['activation_speed']
        standard_health = sage.base_stats['standard_health']
        
        critical_chance += self.skills_affecting['critical_kinesis']*3.0
        damage_increase = self.skills_affecting['clamoring_force']*0.02
        double_proc_chance = self.skills_affecting['telekinetic_momentum']*10.0
        double_proc_multiplier = 30.0
        critical_multiplier += self.skills_affecting['reverberation']*25.0
        
        number_of_ticks = 1
        number_of_critical_ticks = 0
        
        rolled_damage = self.description['coefficient'] * bonus_damage + standard_health * random.uniform(self.description['standard_health_percent_min'], self.description['standard_health_percent_max'])
        base_damage = rolled_damage + damage_increase * rolled_damage
        damage = base_damage
        
        critical_hit = self.is_critical_hit(critical_chance)
        if critical_hit:
            critical_damage = self.return_critical_damage(base_damage, critical_multiplier)
            damage += critical_damage
            number_of_critical_ticks += 1
        else:
            critical_damage = 0
        
        
        double_proc = self.is_double_proc(double_proc_chance)
        if double_proc:
            double_proc_damage = self.return_double_proc_damage(base_damage, double_proc_multiplier)
            number_of_ticks += 1
            double_proc_critical = self.is_critical_hit(critical_chance)
            if double_proc_critical:
                number_of_critical_ticks += 1
                double_proc_critical_damage = self.return_critical_damage(double_proc_damage, critical_multiplier)
                double_proc_damage += double_proc_critical_damage
            damage += double_proc_damage
        else:
            double_proc_damage = None
            double_proc_critical = None        
        clock_step = (1.0 - activation_speed/100.0) * self.description['clock_step']
        
        drs = Damage_Results(ability_name='disturbance', clock_step=clock_step, total_damage=damage, 
                             number_of_ticks=number_of_ticks, 
                             number_of_critical_ticks=number_of_critical_ticks, 
                             main_attack_critical=critical_hit, 
                             double_proc=double_proc, double_proc_damage=double_proc_damage, double_proc_critical=double_proc_critical)
        return drs


class Mind_Crush(Ability):
    def __init__(self, fname='mind_crush.xml'):
        super(Mind_Crush, self).__init__(fname)

    def damage(self, sage, mob):
        '''
        DOT damage calculated in one go
        Not sure when damage_increase is applied, have it before crit at the moment
        '''
        bonus_damage = sage.force_sheet['bonus_damage']
        accuracy = sage.force_sheet['accuracy']
        critical_chance = sage.force_sheet['critical_chance']
        critical_multiplier = sage.force_sheet['critical_multiplier']
        activation_speed = sage.force_sheet['activation_speed']
        standard_health = sage.base_stats['standard_health']
        
        damage_increase = self.skills_affecting['clamoring_force']*0.02
        double_tick_chance = self.skills_affecting['mental_momentum']*10.0
        
        total_damage = 0.0
        
        # initial damage
        initial_damage = 0.0
        base_damage = self.description['coefficient'] * bonus_damage + standard_health * random.uniform(self.description['standard_health_percent_min'], self.description['standard_health_percent_max'])
        damage = base_damage
        damage += damage_increase * damage
        
        critical_hit = self.is_critical_hit(critical_chance)
        if critical_hit:
            critical_damage = self.return_critical_damage(damage, critical_multiplier)
            damage += critical_damage
        else:
            critical_damage = 0
        initial_damage = damage
 
        # dot component       
        total_ticks_damage = 0.0
        critical_ticks_occured = False
        critical_damage_of_tick = 0.0
        number_of_ticks = int(self.description['dot_duration'] / self.description['dot_tick_rate_interval'])
        extra_ticks = 0
        for _ in range(number_of_ticks):
            double_tick_roll = random.random()*100
            if double_tick_roll <= double_tick_chance:
                extra_ticks += 1
        number_of_ticks += extra_ticks
        for _ in range(number_of_ticks):
            base_damage = self.description['dot_coefficient'] * bonus_damage + standard_health * random.uniform(self.description['dot_standard_health_percent_min'], self.description['dot_standard_health_percent_max'])
            damage = base_damage
            damage += damage_increase * damage
    
            critical_hit = self.is_critical_hit(critical_chance)
            if critical_hit:
                critical_damage = self.return_critical_damage(damage, critical_multiplier)
                damage += critical_damage
                critical_ticks_occured = True
                critical_damage_of_tick = critical_damage
            else:
                critical_damage = 0
            total_ticks_damage += damage
        
        total_damage = initial_damage + total_ticks_damage
        clock_step = (1.0 - activation_speed/100.0) * self.description['clock_step']
        
        damage_profile = Damage_Profile('mind_crush', clock_step, total_damage, base_damage, critical_ticks_occured, critical_damage_of_tick, double_proc_hit=False, double_proc_damage=0.0)
        return damage_profile


class Weaken_Mind(Ability):
    def __init__(self, fname='weaken_mind.xml'):
        super(Weaken_Mind, self).__init__(fname)

    def damage(self, sage, mob):
        '''
        DOT damage calculated in one go
        Not sure when damage_increase is applied, have it before crit at the moment
        '''
        bonus_damage = sage.force_sheet['bonus_damage']
        accuracy = sage.force_sheet['accuracy']
        critical_chance = sage.force_sheet['critical_chance']
        critical_multiplier = sage.force_sheet['critical_multiplier']
        activation_speed = sage.force_sheet['activation_speed']
        standard_health = sage.base_stats['standard_health']
        
        damage_increase = self.skills_affecting['empowered_throw']*0.02
        
        total_ticks_damage = 0.0
        critical_ticks_occured = False
        critical_damage_of_tick = 0.0
        number_of_ticks = int(self.description['dot_duration'] / self.description['dot_tick_rate_interval'])
        for _ in range(number_of_ticks):
            base_damage = self.description['dot_coefficient'] * bonus_damage + standard_health * random.uniform(self.description['dot_standard_health_percent_min'], self.description['dot_standard_health_percent_max'])
            damage = base_damage
            damage += damage_increase * damage
    
            critical_hit = self.is_critical_hit(critical_chance)
            if critical_hit:
                critical_damage = self.return_critical_damage(damage, critical_multiplier)
                damage += critical_damage
                critical_ticks_occured = True
                critical_damage_of_tick = critical_damage
            else:
                critical_damage = 0
            total_ticks_damage += damage
        
        clock_step = (1.0 - activation_speed/100.0) * self.description['clock_step']
        
        damage_profile = Damage_Profile('weaken_mind', clock_step, total_ticks_damage, base_damage, critical_ticks_occured, critical_damage_of_tick, double_proc_hit=False, double_proc_damage=0.0)
        return damage_profile


class Telekinetic_Throw(Ability):
    def __init__(self, fname='telekinetic_throw.xml'):
        super(Telekinetic_Throw, self).__init__(fname)

    def damage(self, sage, mob, psychic_projection=True):
        '''
        Not sure when damage_increase is applied, have it before crit at the moment
        '''
        bonus_damage = sage.force_sheet['bonus_damage']
        accuracy = sage.force_sheet['accuracy']
        critical_chance = sage.force_sheet['critical_chance']
        critical_multiplier = sage.force_sheet['critical_multiplier']
        activation_speed = sage.force_sheet['activation_speed']
        standard_health = sage.base_stats['standard_health']

        critical_chance += self.skills_affecting['critical_kinesis']*3.0
        damage_increase = self.skills_affecting['empowered_throw']*0.02
        
        number_of_ticks = 4
        total_ticks_damage = 0.0
        number_of_critical_ticks = 0
        for _ in range(number_of_ticks):
            rolled_damage = self.description['coefficient'] * bonus_damage + standard_health * random.uniform(self.description['standard_health_percent_min'], self.description['standard_health_percent_max'])
            base_damage = rolled_damage + damage_increase * rolled_damage
            damage = base_damage
    
            critical_hit = self.is_critical_hit(critical_chance)
            if critical_hit:
                number_of_critical_ticks += 1
                critical_damage = self.return_critical_damage(base_damage, critical_multiplier)
                damage += critical_damage
            else:
                critical_damage = 0
            total_ticks_damage += damage        
        if psychic_projection:
            clock_step = (1.0 - activation_speed/100.0) * 1.5
        else:
            clock_step = (1.0 - activation_speed/100.0) * self.description['clock_step']
        
        drs = Damage_Results(ability_name='tk_throw', clock_step=clock_step, total_damage=total_ticks_damage, 
                             number_of_ticks=number_of_ticks, 
                             number_of_critical_ticks=number_of_critical_ticks)        
        return drs


class Telekinetic_Wave(Ability):
    def __init__(self, fname='telekinetic_wave.xml'):
        super(Telekinetic_Wave, self).__init__(fname)

    def damage(self, sage, mob):
        '''
        Only single target
        Not sure when damage_increase is applied, have it before crit at the moment
        '''
        bonus_damage = sage.force_sheet['bonus_damage']
        accuracy = sage.force_sheet['accuracy']
        critical_chance = sage.force_sheet['critical_chance']
        critical_multiplier = sage.force_sheet['critical_multiplier']
        activation_speed = sage.force_sheet['activation_speed']
        standard_health = sage.base_stats['standard_health']

        damage_increase = self.skills_affecting['clamoring_force']*0.02
        double_proc_chance = self.skills_affecting['telekinetic_momentum']*10.0
        double_proc_multiplier = 30.0
        critical_multiplier += self.skills_affecting['reverberation']*25.0
        
        rolled_damage = self.description['coefficient'] * bonus_damage + standard_health * random.uniform(self.description['standard_health_percent_min'], self.description['standard_health_percent_max'])
        base_damage = rolled_damage + damage_increase * rolled_damage
        damage = base_damage

        number_of_ticks = 1
        number_of_critical_ticks = 0
        
        critical_hit = self.is_critical_hit(critical_chance)
        if critical_hit:
            number_of_critical_ticks += 1
            critical_damage = self.return_critical_damage(base_damage, critical_multiplier)
            damage += critical_damage
        else:
            critical_damage = 0.0
        
        double_proc = self.is_double_proc(double_proc_chance)
        if double_proc:
            number_of_ticks += 1
            double_proc_damage = self.return_double_proc_damage(base_damage, double_proc_multiplier)
            double_proc_critical = self.is_critical_hit(critical_chance)
            if double_proc_critical:
                number_of_critical_ticks += 1
                double_proc_critical_damage = self.return_critical_damage(double_proc_damage, critical_multiplier)
                double_proc_damage += double_proc_critical_damage
            damage += double_proc_damage
        else:
            double_proc_damage = None
            double_proc_critical = None
        
        clock_step = (1.0 - activation_speed/100.0) * self.description['clock_step']
        
        drs = Damage_Results(ability_name='tk_wave', clock_step=clock_step, total_damage=damage, 
                             number_of_ticks=number_of_ticks, 
                             number_of_critical_ticks=number_of_critical_ticks, 
                             main_attack_critical=critical_hit, 
                             double_proc=double_proc, double_proc_damage=double_proc_damage, double_proc_critical=double_proc_critical)        
        return drs


class Turbulence(Ability):
    def __init__(self, fname='turbulence.xml'):
        super(Turbulence, self).__init__(fname)

    def damage(self, sage, mob, autocrit=True):
        '''
        Not sure when damage_increase is applied, have it before crit at the moment
        '''
        bonus_damage = sage.force_sheet['bonus_damage']
        accuracy = sage.force_sheet['accuracy']
        critical_chance = sage.force_sheet['critical_chance']
        critical_multiplier = sage.force_sheet['critical_multiplier']
        activation_speed = sage.force_sheet['activation_speed']
        standard_health = sage.base_stats['standard_health']        
        if autocrit:
            critical_chance = 101.00
        damage_increase = self.skills_affecting['clamoring_force']*0.02
        double_proc_chance = self.skills_affecting['mental_momentum']*10.0
        double_proc_multiplier = 30.0
        critical_multiplier += self.skills_affecting['reverberation']*25.0
        
        number_of_ticks = 1
        number_of_critical_ticks = 0
        
        rolled_damage = self.description['coefficient'] * bonus_damage + standard_health * random.uniform(self.description['standard_health_percent_min'], self.description['standard_health_percent_max'])
        base_damage = rolled_damage + damage_increase * rolled_damage
        damage = base_damage
        
        critical_hit = self.is_critical_hit(critical_chance)
        if critical_hit:
            number_of_critical_ticks += 1
            critical_damage = self.return_critical_damage(base_damage, critical_multiplier)
            damage += critical_damage
        else:
            critical_damage = 0.0
        
        double_proc = self.is_double_proc(double_proc_chance)
        if double_proc:
            number_of_ticks += 1
            double_proc_damage = self.return_double_proc_damage(base_damage, double_proc_multiplier)
            double_proc_critical = self.is_critical_hit(critical_chance)
            if double_proc_critical:
                number_of_critical_ticks += 1
                double_proc_critical_damage = self.return_critical_damage(double_proc_damage, critical_multiplier)
                double_proc_damage += double_proc_critical_damage
            damage += double_proc_damage
        else:
            double_proc_damage = None
            double_proc_critical = None        
        clock_step = (1.0 - activation_speed/100.0) * self.description['clock_step']
        
        drs = Damage_Results(ability_name='turbulence', clock_step=clock_step, total_damage=damage, 
                             number_of_ticks=number_of_ticks, 
                             number_of_critical_ticks=number_of_critical_ticks, 
                             main_attack_critical=critical_hit, 
                             double_proc=double_proc, double_proc_damage=double_proc_damage, double_proc_critical=double_proc_critical)
        return drs


class Project(Ability):
    def __init__(self, fname='project.xml'):
        super(Project, self).__init__(fname)

    def damage(self, sage, mob):
        '''
        Not sure when damage_increase is applied, have it before crit at the moment
        '''
        bonus_damage = sage.force_sheet['bonus_damage']
        accuracy = sage.force_sheet['accuracy']
        critical_chance = sage.force_sheet['critical_chance']
        critical_multiplier = sage.force_sheet['critical_multiplier']
        activation_speed = sage.force_sheet['activation_speed']
        standard_health = sage.base_stats['standard_health']

        damage_increase = self.skills_affecting['empowered_throw']*0.02
        double_proc_chance = self.skills_affecting['upheaval']*15.0
        double_proc_multiplier = 50.0
        
        number_of_ticks = 1
        number_of_critical_ticks = 0
        
        rolled_damage = self.description['coefficient'] * bonus_damage + standard_health * random.uniform(self.description['standard_health_percent_min'], self.description['standard_health_percent_max'])
        base_damage = rolled_damage + damage_increase * rolled_damage
        damage = base_damage
        
        critical_hit = self.is_critical_hit(critical_chance)
        if critical_hit:
            number_of_critical_ticks += 1
            critical_damage = self.return_critical_damage(damage, critical_multiplier)
            damage += critical_damage
        else:
            critical_damage = 0
        
        double_proc = self.is_double_proc(double_proc_chance)
        if double_proc:
            number_of_ticks += 1
            double_proc_damage = self.return_double_proc_damage(damage, double_proc_multiplier)
            double_proc_critical = self.is_critical_hit(critical_chance)
            if double_proc_critical:
                number_of_critical_ticks += 1
                double_proc_critical_damage = self.return_critical_damage(double_proc_damage, critical_multiplier)
                double_proc_damage += double_proc_critical_damage

            damage += double_proc_damage
        else:
            double_proc_damage = None
            double_proc_critical = None
        
        clock_step = (1.0 - activation_speed/100.0) * self.description['clock_step']
        
        drs = Damage_Results(ability_name='project', clock_step=clock_step, total_damage=damage, 
                             number_of_ticks=number_of_ticks, 
                             number_of_critical_ticks=number_of_critical_ticks, 
                             main_attack_critical=critical_hit, 
                             double_proc=double_proc, double_proc_damage=double_proc_damage, double_proc_critical=double_proc_critical)
        return drs


class Rotation(object):
    def __init__(self, fname='rotation.xml'):
        tree = ET.parse(fname)
        self.root = tree.getroot()
        self.template_rotation = ast.literal_eval(self.root.find('template').text)
        self.repetitions = int(self.root.find('repetitions').text)
        self.am = {'d':'disturbance',
                   'p':'project',
                   't':'turbulence',
                   'tkw':'tk_wave',
                   'tkt':'tk_throw',
                   'wm':'weaken_mind',
                   'mc':'mind_crush'}        
        

if __name__ == '__main__':
    sage = Sage()
    mob = Mob()
    rot = Rotation()
    
    clock = 0.0
    total_damage = 0.0
    dprofs = []
    for _ in range(rot.repetitions):
        for a in rot.template_rotation:
            s = rot.am[a]
            dprof = sage.abilities[s].damage(sage, mob)
            dprofs.append(dprof)
            clock += dprof.clock_step
            total_damage += dprof.total_damage
    dps = total_damage / clock
    print 'You did', total_damage, 'damage in', clock, 'secs.'
    print 'DPS:', dps
    print
    print 'Thank you for trying it. Leave comments/bugs in the following thread:'
    print 'http://www.swtor.com/community/showthread.php?t=745689'
    
#     print 'disturbance:', sage.abilities['disturbance'].damage(sage, mob).total_damage
#     print 'project:', sage.abilities['project'].damage(sage, mob).total_damage
#     print 'tk_throw:', sage.abilities['tk_throw'].damage(sage, mob).total_damage
#     print 'tk_wave:', sage.abilities['tk_wave'].damage(sage, mob).total_damage
#     print 'turbulence:', sage.abilities['turbulence'].damage(sage, mob).total_damage
#     print 'weaken_mind:', sage.abilities['weaken_mind'].damage(sage, mob).total_damage
#     print 'mind_crush:', sage.abilities['mind_crush'].damage(sage, mob).total_damage
