from kameleon_rks.densities.banana import log_banana_pdf, sample_banana
from kameleon_rks.densities.gaussian import mvnorm
from kameleon_rks.examples.plotting import visualize_scatter
from kameleon_rks.smc.mini_pmc import mini_pmc
from kameleon_rks.proposals.Kameleon import OracleKameleon, Kameleon, \
    gamma_median_heuristic
from kameleon_rks.proposals.Langevin import StaticLangevin, AdaptiveLangevin
from kameleon_rks.proposals.Metropolis import StaticMetropolis, \
    AdaptiveMetropolis
from kameleon_rks.tools.log import Log
import matplotlib.pyplot as plt
from kameleon_mcmc.kernel.PolynomialKernel import PolynomialKernel
import numpy as np
import scipy.stats as stats


def one_over_4th_root_t_schedule(t):
    return 1. / (1 + t)**(0.24)

def get_StaticMetropolis_instance(D, target_log_pdf):
    
    step_size = 8.
    schedule = one_over_4th_root_t_schedule
    acc_star = 0.234
    instance = StaticMetropolis(D, target_log_pdf, step_size, schedule, acc_star)
    
    return instance

def get_AdaptiveMetropolis_instance(D, target_log_pdf):
    
    step_size = 1.
    schedule = one_over_4th_root_t_schedule
    acc_star = 0.234
    gamma2 = 0.1
    instance = AdaptiveMetropolis(D, target_log_pdf, step_size, gamma2, schedule, acc_star)
    
    return instance

def get_OracleKameleon_instance(D, target_log_pdf):
    
    step_size = 30.
    schedule = one_over_4th_root_t_schedule
    acc_star = 0.234
    gamma2 = 0.1
    n = 500
    
    Z = sample_banana(N=n, D=D, bananicity=0.03, V=100)
    
    kernel_sigma = 1. / gamma_median_heuristic(Z)
    instance = OracleKameleon(D, target_log_pdf, n, kernel_sigma, step_size, gamma2, schedule, acc_star)
    instance.set_batch(Z)
    
    return instance
    
def get_StaticKameleon_instance(D, target_log_pdf):
    
    step_size = 30.
    schedule = one_over_4th_root_t_schedule
    acc_star = 0.234
    gamma2 = 0.1
    n = 500
    
    Z = sample_banana(N=n, D=D, bananicity=0.03, V=100)
    
    kernel_sigma = 1. / gamma_median_heuristic(Z)
    instance = StaticKameleon(D, target_log_pdf, n, kernel_sigma, step_size, gamma2, schedule, acc_star)
    instance.set_batch(Z)
    
    return instance



def get_StaticLangevin_instance(D, target_log_pdf, target_grad):
    
    step_size = 1.
    schedule = one_over_4th_root_t_schedule
    acc_star = 0.234
    
    instance = StaticLangevin(D, target_log_pdf, target_grad, step_size, schedule, acc_star)
    
    return instance

def get_AdaptiveLangevin_instance(D, target_log_pdf, target_grad):
    
    step_size = 1.
    schedule = one_over_4th_root_t_schedule
    acc_star = 0.234
    gamma2 = 0.1
    
    instance = AdaptiveLangevin(D, target_log_pdf, target_grad, step_size, gamma2, schedule, acc_star)
    
    return instance

if __name__ == '__main__':
    Log.set_loglevel(20)
    D = 2
    
    bananicity = 0.03
    V = 100
    Z = sample_banana(700, D, bananicity, V)
    target_log_pdf = lambda x: log_banana_pdf(x, bananicity, V, compute_grad=False)
    target_grad = lambda x: log_banana_pdf(x, bananicity, V, compute_grad=True)

    samplers = [
                get_StaticMetropolis_instance(D, target_log_pdf),
                get_OracleKameleon_instance(D, target_log_pdf),
                get_AdaptiveMetropolis_instance(D, target_log_pdf),
                get_StaticLangevin_instance(D, target_log_pdf, target_grad),
                get_AdaptiveLangevin_instance(D, target_log_pdf, target_grad),
                ]
    #SMC sampler
    kern = PolynomialKernel(3)
    for sampler in samplers:
        # MCMC parameters, feel free to increase number of iterations
        start = np.zeros(D)
        num_iter = 1000
        
        # run SMC with adaptive bridge  
        bridge_start = mvnorm(np.zeros(D),np.eye(D)*np.sqrt(2.8/D))                    
        samples, log_target_densities, times = mini_pmc(sampler, start, num_iter, 10, D)
                    
        visualize_scatter(samples)
        mmd = kern.estimateMMD(Z,samples)
        Log.get_logger().info('MMD %.2f'%mmd)
        plt.suptitle("%s" % \
                     (sampler.__class__.__name__,))
    plt.show()

