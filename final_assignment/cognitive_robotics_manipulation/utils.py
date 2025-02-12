import random
from datetime import datetime
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import FancyBboxPatch


class YcbObjects:
    def __init__(self, load_path, mod_orn=None, mod_stiffness=None, exclude=None):
        self.load_path = load_path
        self.mod_orn = mod_orn
        self.mod_stiffness = mod_stiffness
        with open(load_path + '/obj_list.txt') as f:
            lines = f.readlines()
            self.obj_names = [line.rstrip('\n') for line in lines]
        if exclude is not None:
            for obj_name in exclude:
                self.obj_names.remove(obj_name)

    def shuffle_objects(self):
        random.shuffle(self.obj_names)

    def get_obj_path(self, obj_name):
        return f'{self.load_path}/Ycb{obj_name}/model.urdf'

    def check_mod_orn(self, obj_name):
        if self.mod_orn is not None and obj_name in self.mod_orn:
            return True
        return False

    def check_mod_stiffness(self, obj_name):
        if self.mod_stiffness is not None and obj_name in self.mod_stiffness:
            return True
        return False

    def get_obj_info(self, obj_name):
        return self.get_obj_path(obj_name), self.check_mod_orn(obj_name), self.check_mod_stiffness(obj_name)

    def get_n_first_obj_info(self, n):
        info = []
        for obj_name in self.obj_names[:n]:
            info.append(self.get_obj_info(obj_name))
        return info


class PackPileData:

    def __init__(self, num_obj, trials, save_path, scenario):
        self.num_obj = num_obj
        self.trials = trials
        self.save_path = save_path

        if not os.path.exists(save_path):
            os.mkdir(save_path)
        now = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        self.save_dir = f'{save_path}/{now}_{scenario}'
        os.mkdir(self.save_dir)

        self.tries = 0
        self.succes_grasp = 0
        self.succes_target = 0

    def add_try(self):
        self.tries += 1

    def add_succes_target(self):
        self.succes_target += 1

    def add_succes_grasp(self):
        self.succes_grasp += 1

    def summarize(self):
        grasp_acc = self.succes_grasp / self.tries
        target_acc = self.succes_target / self.tries
        perc_obj_cleared = self.succes_target / (self.trials * self.num_obj)

        with open(f'{self.save_dir}/summary.txt', 'w') as f:
            f.write(
                f'Stats for {self.num_obj} objects out of {self.trials} trials\n')
            f.write(
                f'Manipulation success rate = {target_acc:.3f} ({self.succes_target}/{self.tries})\n')
            f.write(
                f'Grasp success rate = {grasp_acc:.3f} ({self.succes_grasp}/{self.tries})\n')
            f.write(
                f'Percentage of objects removed from the workspace = {perc_obj_cleared} ({self.succes_target}/{(self.trials * self.num_obj)})\n')

       

        # plot the obtained results
        import numpy as np
        results = [grasp_acc, target_acc, perc_obj_cleared]
        metrics = ['grasp', 'manipulation', '% removed from WS']

        x_pos = np.arange(len(metrics))
        
        # Create bars and choose color
        fig,ax = plt.subplots()
        ax.set_axisbelow(True)
        plt.grid(color='#95a5a6', linestyle='-', linewidth=1, alpha=0.25)
        plt.ylim(0, 1)
        # Add title and axis names        
        plt.rc('axes', titlesize=16)     # fontsize of the axes title
        plt.title(f'Summary of performance for {self.trials} runs')
        plt.xlabel('')
        plt.ylabel('Succes rate (%)', fontsize=16)
        plt.setp(ax.get_xticklabels(), fontsize=12)
        plt.setp(ax.get_yticklabels(), fontsize=12)
        plt.xticks(x_pos, metrics)
        plt.bar(x_pos, results)
        # save graph
        plt.savefig(self.save_dir+'/plot.png')

    def summarize_multi_data(self, **kwargs):

        plot_type = kwargs.get('plot_type','single')
        model_name = kwargs.get('m_name')
        
        if plot_type == 'single':
            
            grasp_acc = self.succes_grasp / self.tries
            target_acc = self.succes_target / self.tries
            perc_obj_cleared = self.succes_target / (self.trials * self.num_obj)
            self.data.append([grasp_acc, target_acc, perc_obj_cleared])
            self.models.append(model_name)
            
            with open(f'{self.save_dir}/summary_'+model_name+'.txt', 'w') as f:
                f.write(
                    f'Stats for {self.num_obj} objects out of {self.trials} trials\n')
                f.write(
                    f'Manipulation success rate = {target_acc:.3f} ({self.succes_target}/{self.tries})\n')
                f.write(
                    f'Grasp success rate = {grasp_acc:.3f} ({self.succes_grasp}/{self.tries})\n')
                f.write(
                    f'Percentage of objects removed from the workspace = {perc_obj_cleared} ({self.succes_target}/{(self.trials * self.num_obj)})\n')
            
            results = [grasp_acc, target_acc, perc_obj_cleared]
       

        # plot the obtained results
        import numpy as np
        
        metrics = ['grasp', 'manipulation', 'removed from WS']

        x_pos = np.arange(len(metrics))
        
        # Create bars and choose color
        fig,ax = plt.subplots()
        ax.set_axisbelow(True)
        plt.grid(color='#95a5a6', linestyle='-', linewidth=1, alpha=0.25)
        plt.ylim(0, 1)
        # Add title and axis names        
        plt.rc('axes', titlesize=16)     # fontsize of the axes title
        plt.title(f'Summary of performance for {self.trials} runs')
        plt.xlabel('')
        plt.ylabel('Succes rate (%)', fontsize=16)
        plt.setp(ax.get_xticklabels(), fontsize=12)
        plt.setp(ax.get_yticklabels(), fontsize=12)
        plt.xticks(x_pos, metrics)
        
        if plot_type == 'single':
            plt.bar(x_pos, results)
            # save graph
            plt.savefig(self.save_dir+'/'+model_name+'_plot.png')
        
        if plot_type == 'multiple':
            offset = 0
            print(self.data)
            print(len(self.data))
            for data in range(len(self.data)):
                plt.bar(x_pos+offset, self.data[data], 0.2)
                offset+=0.2
            
            plt.legend(self.models)    
            # save graph
            plt.savefig(self.save_dir+'/m_plot.png')
        
               
            


class IsolatedObjData:

    def __init__(self, obj_names, trials, save_path):
        self.obj_names = obj_names
        self.trials = trials
        self.succes_target = dict.fromkeys(obj_names, 0)
        self.succes_grasp = dict.fromkeys(obj_names, 0)
        self.tries = dict.fromkeys(obj_names, 0)

        if not os.path.exists(save_path):
            os.mkdir(save_path)
        now = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        self.save_dir = f'{save_path}/{now}_iso_obj'
        os.mkdir(self.save_dir)

    def add_succes_target(self, obj_name):
        self.succes_target[obj_name] += 1

    def add_succes_grasp(self, obj_name):
        self.succes_grasp[obj_name] += 1

    def add_try(self, obj_name):
        self.tries[obj_name] += 1

    # def write_json(self):
    #     data_tries = json.dumps(self.tries)
    #     data_target = json.dumps(self.succes_target)
    #     data_grasp = json.dumps(self.succes_grasp)
    #     f = open(self.save_dir+'/data_tries.json', 'w')
    #     f.write(data_tries)
    #     f.close()
    #     f = open(self.save_dir+'/data_target.json', 'w')
    #     f.write(data_target)
    #     f.close()
    #     f = open(self.save_dir+'/data_grasp.json', 'w')
    #     f.write(data_grasp)
    #     f.close()

    def write_json(self, modelname):
        data_tries = json.dumps(self.tries)
        data_target = json.dumps(self.succes_target)
        data_grasp = json.dumps(self.succes_grasp)
        f = open(self.save_dir+'/'+modelname+'_data_tries.json', 'w')
        f.write(data_tries)
        f.close()
        f = open(self.save_dir+'/'+modelname+'_data_target.json', 'w')
        f.write(data_target)
        f.close()
        f = open(self.save_dir+'/'+modelname+'_data_grasp.json', 'w')
        f.write(data_grasp)
        f.close()

def plot(path, tries, target, grasp, trials):
    succes_rate = dict.fromkeys(tries.keys())
    for obj in succes_rate.keys():
        t = tries[obj]
        if t == 0:
            t = 1
        acc_target = target[obj] / t
        acc_grasp = grasp[obj] / t
        succes_rate[obj] = (acc_target, acc_grasp)

    plt.rc('axes', titlesize=13)     # fontsize of the axes title
    plt.rc('axes', labelsize=12)    # fontsize of the x and y labels

    df = pd.DataFrame(succes_rate).T
    df.columns = ['Manipulation', 'Grasp']
    df = df.sort_values(by='Manipulation', ascending=True)
    ax = df.plot(kind='bar', color=['#88CCEE', '#CC6677'])
    # ax = df.plot(kind='bar', color=['b', 'r'])

    plt.xlabel('objects')
    plt.ylabel('succes rate (%)')
    plt.title(
        f'Succes rate for object grasping and manipulation | {trials} runs')
    plt.grid(color='#95a5a6', linestyle='-', linewidth=1, axis='y', alpha=0.5)
    ax.set_axisbelow(True)
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45,
             ha="right", rotation_mode="anchor")
    plt.locator_params(axis="y", nbins=11)

    plt.legend(loc='lower right')
    plt.subplots_adjust(bottom=0.28)

    plt.savefig(path+'/plot.png')


def write_summary(path, tries, target, grasp):
    with open(path+'/summary.txt', 'w') as f:
        total_tries = sum(tries.values())
        total_target = sum(target.values())
        total_grasp = sum(grasp.values())
        f.write('Total:\n')
        f.write(
            f'Grasp acc={total_grasp/total_tries:.3f} ({total_grasp}/{total_tries}) --- Manipulation acc={total_target/total_tries:.3f} ({total_target}/{total_tries}) \n')
        f.write('\n')
        f.write("Accuracy per object:\n")
        for obj in tries.keys():
            n_tries = tries[obj]
            n_t = target[obj]
            n_g = grasp[obj]
            if n_tries == 0:
                f.write(
                    f'{obj}: Grasp acc=0.000 (0/0) --- Manipulation acc=0.000 (0/0) \n')
            else:   
                f.write(
                    f'{obj}: Grasp acc={n_g/n_tries:.3f} ({n_g}/{n_tries}) --- Manipulation acc={n_t/n_tries:.3f} ({n_t}/{n_tries}) \n')


def summarize(path, trials,modelname):
    # with open(path+'/data_tries.json') as data:
    #     tries = json.load(data)
    # with open(path+'/data_target.json') as data:
    #     target = json.load(data)
    # with open(path+'/data_grasp.json') as data:
    #     grasp = json.load(data)
    with open(path+'/'+modelname+'_data_tries.json') as data:
        tries = json.load(data)
    with open(path+'/'+modelname+'_data_target.json') as data:
        target = json.load(data)
    with open(path+'/'+modelname+'_data_grasp.json') as data:
        grasp = json.load(data)

    plot(path, tries, target, grasp, trials)
    write_summary(path, tries, target, grasp)


def plot_specific_model(path, tries, target, grasp, trials, modelname):
    succes_rate = dict.fromkeys(tries.keys())
    for obj in succes_rate.keys():
        t = tries[obj]
        if t == 0:
            t = 1
        acc_target = target[obj] / t
        acc_grasp = grasp[obj] / t
        succes_rate[obj] = (acc_target, acc_grasp)

    plt.rc('axes', titlesize=13)     # fontsize of the axes title
    plt.rc('axes', labelsize=12)    # fontsize of the x and y labels

    df = pd.DataFrame(succes_rate).T
    df.columns = ['Manipulation', 'Grasp']
    df = df.sort_values(by='Manipulation', ascending=True)
    ax = df.plot(kind='bar', color=['#88CCEE', '#CC6677'])
    # ax = df.plot(kind='bar', color=['b', 'r'])

    plt.xlabel('Object name')
    plt.ylabel('Succes rate (%)')
    plt.title(
        f'Succes rate for object grasping and manipulation | {trials} runs')
    plt.grid(color='#95a5a6', linestyle='-', linewidth=1, axis='y', alpha=0.5)
    ax.set_axisbelow(True)
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45,
             ha="right", rotation_mode="anchor")
    plt.locator_params(axis="y", nbins=11)

    plt.legend(loc='lower right')
    plt.subplots_adjust(bottom=0.28)

    plt.savefig(path+'/'+modelname+'_plot.png')


def write_summary_specific_model(path, tries, target, grasp, modelname):
    with open(path+'/'+modelname+'_summary.txt', 'w') as f:
        total_tries = sum(tries.values())
        total_target = sum(target.values())
        total_grasp = sum(grasp.values())
        f.write('Total:\n')
        f.write(
            f'Target acc={total_target/total_tries:.3f} ({total_target}/{total_tries}) Grasp acc={total_grasp/total_tries:.3f} ({total_grasp}/{total_tries})\n')
        f.write('\n')
        f.write("Accuracy per object:\n")
        for obj in tries.keys():
            n_tries = tries[obj]
            n_t = target[obj]
            n_g = grasp[obj]
            f.write(
                f'{obj}: Target acc={n_t/n_tries:.3f} ({n_t}/{n_tries}) Grasp acc={n_g/n_tries:.3f} ({n_g}/{n_tries})\n')


def summarize_specific_model(path, trials, modelname):
    with open(path+'/'+modelname+'_data_tries.json') as data:
        tries = json.load(data)
    with open(path+'/'+modelname+'_data_target.json') as data:
        target = json.load(data)
    with open(path+'/'+modelname+'_data_grasp.json') as data:
        grasp = json.load(data)

    plot_specific_model(path, tries, target, grasp, trials, modelname)
    write_summary_specific_model(path, tries, target, grasp, modelname)
