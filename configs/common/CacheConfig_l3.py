# Copyright (c) 2012-2013, 2015-2016 ARM Limited
# All rights reserved
#
# The license below extends only to copyright in the software and shall
# not be construed as granting a license to any other intellectual
# property including but not limited to intellectual property relating
# to a hardware implementation of the functionality of the software
# licensed hereunder.  You may use the software subject to the license
# terms below provided that you ensure that this notice is replicated
# unmodified and in its entirety in all distributions of the software,
# modified or unmodified, in source code or in binary form.
#
# Copyright (c) 2010 Advanced Micro Devices, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Lisa Hsu

# Configure the M5 cache hierarchy config in one place
#

import m5
from m5.objects import *
#from Caches import *
from Caches_l3 import *

def config_cache(options, system):
    if options.external_memory_system and (options.caches or options.l2cache):
        print "External caches and internal caches are exclusive options.\n"
        sys.exit(1)

    if options.external_memory_system:
        ExternalCache = ExternalCacheFactory(options.external_memory_system)

    if options.cpu_type == "arm_detailed":
        try:
            from O3_ARM_v7a import *
        except:
            print "arm_detailed is unavailable. Did you compile the O3 model?"
            sys.exit(1)

        dcache_class, icache_class, l2_cache_class, l3_cache_calss, walk_cache_class = \
            O3_ARM_v7a_DCache, O3_ARM_v7a_ICache, O3_ARM_v7aL2, O3_ARM_v7aL3, O3_ARM_v7aWalkCache
    else:
        dcache_class, icache_class, l2_cache_class, l3_cache_class,walk_cache_class = \
            L1_DCache, L1_ICache, L2Cache, L3Cache, None

        if buildEnv['TARGET_ISA'] == 'x86':
            walk_cache_class = PageTableWalkerCache

    # Set the cache line size of the system
    system.cache_line_size = options.cacheline_size

    # If elastic trace generation is enabled, make sure the memory system is
    # minimal so that compute delays do not include memory access latencies.
    # Configure the compulsory L1 caches for the O3CPU, do not configure
    # any more caches.
    if options.l3cache and options.elastic_trace_en:
        fatal("When elastic trace is enabled, do not configure L2 caches.")
    if options.l3cache:
    	system.l3=l3_cache_class(clk_domain=system.cpu_clk_domain,
                           size=options.l3_size,
                           assoc=options.l3_assoc,
                           two_step_encoding = True)
        system.tol3bus=L3XBar(clk_domain = system.cpu_clk_domain)
        system.l3.cpu_side = system.tol3bus.master
        system.l3.mem_side = system.membus.slave
	if options.l3_tags == 1:
		system.l3.tags = CAR()
	if options.l3_tags == 2:
		system.l3.tags = MLC(loc_weight = 0)
	if options.l3_tags == 3:
		system.l3.tags = MLC(loc_weight = 510, flipSize = 0, options = 0 )
	system.l3.tags.two_step_encoding = True

    for i in xrange(options.num_cpus):
        if options.caches:
            icache = icache_class(size=options.l1i_size,
                                  assoc=options.l1i_assoc)
            dcache = dcache_class(size=options.l1d_size,
                                  assoc=options.l1d_assoc)

            if buildEnv['TARGET_ISA'] == 'x86':
                system.cpu[i].addPrivateSplitL1Caches(icache, dcache,
                             PageTableWalkerCache(),
                             PageTableWalkerCache())
            else:
                system.cpu[i].addPrivateSplitL1Caches(icache, dcache)
        system.cpu[i].createInterruptController()


    	if options.l2cache:
        # Provide a clock for the L2 and the L1-to-L2 bus here as they
        # are not connected using addTwoLevelCacheHierarchy. Use the
        # same clock as the CPUs.
        	system.cpu[i].l2 = l2_cache_class(clk_domain=system.cpu_clk_domain,
                                   size=options.l2_size,
                                   assoc=options.l2_assoc)

        	system.cpu[i].tol2bus = L2XBar(clk_domain = system.cpu_clk_domain)
        	system.cpu[i].l2.cpu_side = system.cpu[i].tol2bus.master
        	system.cpu[i].l2.mem_side = system.tol3bus.slave


    	if options.l3cache:
	    system.cpu[i].connectAllPorts(system.cpu[i].tol2bus, system.membus)
    	else:
		if options.l2cache:
			system.cpu[i].connectAllPorts(system.tol2bus, system.membus)
		elif options.external_memory_system:
			system.cpu[i].connectUncachedPorts(system.membus)
		else:
			system.cpu[i].connectAllPorts(system.membus)

        # Add a snoop filter to the membus if there are caches above it
       # if (options.l2cache or options.caches) and \
       # (system.membus.snoop_filter == NULL):
       #     system.membus.snoop_filter = SnoopFilter()

    return system

# ExternalSlave provides a "port", but when that port connects to a cache,
# the connecting CPU SimObject wants to refer to its "cpu_side".
# The 'ExternalCache' class provides this adaptation by rewriting the name,
# eliminating distracting changes elsewhere in the config code.
class ExternalCache(ExternalSlave):
    def __getattr__(cls, attr):
        if (attr == "cpu_side"):
            attr = "port"
        return super(ExternalSlave, cls).__getattr__(attr)

    def __setattr__(cls, attr, value):
        if (attr == "cpu_side"):
            attr = "port"
        return super(ExternalSlave, cls).__setattr__(attr, value)

def ExternalCacheFactory(port_type):
    def make(name):
        return ExternalCache(port_data=name, port_type=port_type,
                             addr_ranges=[AllMemory])
    return make
