#
#   This file is part of do-mpc
#
#   do-mpc: An environment for the easy, modular and efficient implementation of
#        robust nonlinear model predictive control
#
#   Copyright (c) 2014-2019 Sergio Lucia, Alexandru Tatulea-Codrean
#                        TU Dortmund. All rights reserved
#
#   do-mpc is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as
#   published by the Free Software Foundation, either version 3
#   of the License, or (at your option) any later version.
#
#   do-mpc is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with do-mpc.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import matplotlib.pyplot as plt
from casadi import *
from casadi.tools import *
import pdb
import sys
import time
sys.path.append('../../')
import do_mpc

from template_model import template_model
from template_mpc import template_mpc
from template_simulator import template_simulator
from template_mhe import template_mhe

model = template_model()
mpc = template_mpc(model)
simulator = template_simulator(model)
mhe = template_mhe(model)


"""
Set initial state
"""
np.random.seed(99)

# Use different initial state for the true system (simulator) and for MHE / MPC
x0_true = np.random.rand(model.n_x)-0.5
x0 = np.zeros(model.n_x)
mpc.set_initial_state(x0, reset_history=True)
simulator.set_initial_state(x0_true, reset_history=True)
mhe.set_initial_state(x0, p_est0 = np.array([1e-4]), reset_history=True)


"""
Setup graphic:
"""
color = plt.rcParams['axes.prop_cycle'].by_key()['color']

fig, ax = plt.subplots(5,1, sharex=True, figsize=(10, 9))

mpc_plot = do_mpc.graphics.Graphics()
mhe_plot = do_mpc.graphics.Graphics()

ax[0].set_title('controlled position:')
mpc_plot.add_line('_x', 'phi_2', ax[0])
mpc_plot.add_line('_tvp', 'phi_2_set', ax[0], color=color[0], linestyle='--', alpha=0.5)

ax[1].set_title('uncontrolled position:')
mpc_plot.add_line('_x', 'phi_1', ax[1])
mpc_plot.add_line('_x', 'phi_3', ax[1])

ax[2].set_title('Inputs:')
mpc_plot.add_line('_u', 'phi_m_set', ax[2])

ax[3].set_title('Estimated angular velocity:')
mhe_plot.add_line('_x', 'dphi', ax[3])
ax[4].set_title('Estimated parameters:')
mhe_plot.add_line('_p', 'Theta_1', ax[4])

ax[0].set_ylabel('disc \n angle [rad]')
ax[1].set_ylabel('disc \n angle [rad]')
ax[2].set_ylabel('motor \n angle [rad]')
ax[3].set_ylabel('angle \n velocity [rad/2]')
ax[4].set_ylabel('mass inertia')
ax[3].set_xlabel('time [s]')



# fig, ax, graphics = do_mpc.graphics.default_plot(model)

fig.tight_layout()
plt.ion()

"""
Run MPC main loop:
"""

for k in range(200):
    u0 = mpc.make_step(x0)
    y_next = simulator.make_step(u0)
    x0 = mhe.make_step(y_next)


    if True:
        mpc_plot.reset_axes()
        mhe_plot.reset_axes()
        mpc_plot.plot_results(mpc.data, linewidth=3)
        mpc_plot.plot_predictions(mpc.data, mpc.opt_x_num, mpc.opt_aux_num, linestyle='--', linewidth=1)

        mhe_plot.plot_results(simulator.data, linewidth=6, alpha = 0.4)
        mhe_plot.plot_results(mhe.data, linewidth=3, alpha = 1)

        for ax_i in ax:
            ax_i.axvline(1.0)

        plt.show()
        input('next step')

mpc_plot.plot_results(mpc.data, linewidth=3)
mhe_plot.plot_results(simulator.data, linewidth=6, alpha = 0.4)
mhe_plot.plot_results(mhe.data, linewidth=3, alpha = 1)
plt.show()
input('Press any key to exit.')
