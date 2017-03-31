# Copyright (c) 2012-2013 ARM Limited
# All rights reserved.
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
# Authors: Prakash Ramrakhyani

from m5.params import *
from m5.proxy import *
from ClockedObject import ClockedObject

class BaseTags(ClockedObject):
    type = 'BaseTags'
    abstract = True
    cxx_header = "mem/cache/tags/base.hh"
    # Get the size from the parent (cache)
    size = Param.MemorySize(Parent.size, "capacity in bytes")

    # Get the block size from the parent (system)
    block_size = Param.Int(Parent.cache_line_size, "block size in bytes")

    # Get the hit latency from the parent (cache)
    hit_latency = Param.Cycles(Parent.hit_latency,
                               "The hit latency for this cache")
    two_step_encoding = Param.Bool(False, "Two step encoding for MLC to increase endurance")

class BaseSetAssoc(BaseTags):
    type = 'BaseSetAssoc'
    abstract = True
    cxx_header = "mem/cache/tags/base_set_assoc.hh"
    assoc = Param.Int(Parent.assoc, "associativity")
    sequential_access = Param.Bool(Parent.sequential_access,
        "Whether to access tags and data sequentially")

class LRU(BaseSetAssoc):
    type = 'LRU'
    cxx_class = 'LRU'
    cxx_header = "mem/cache/tags/lru.hh"

class CAR(BaseSetAssoc):
    type = 'CAR'
    cxx_class = 'CAR'
    cxx_header = "mem/cache/tags/car.hh"
    #shifSize = Param.Int(Parent.shift_size, "shift size in bytes")
    #flipSize = Param.Int(Parent.flip_size, "flip size in bytes")
    #encodingSize = Param.Int(Parent.encoding_size, "encoding size in bytes")
    #thres = Param.Int(Parent.encoding_threshold, "encoding threshold out of 64 ")

class MLC(BaseSetAssoc):
    type = 'MLC'
    cxx_class = 'MLC'
    cxx_header = "mem/cache/tags/mlc.hh"
    #shifSize = Param.Int(Parent.shift_size, "shift size in bytes")
    flipSize = Param.Int(4, "flip size in bytes")
    encodingSize = Param.Int(4, "encoding size in bytes")
    loc_weight = Param.Int(0, "location weight")
    diverse_weight = Param.Float(13.5, "diverse weight")
    thres = Param.Int(12, "encoding threshold out of 64 ")
    options = Param.Int(0, "options of scheme")

class RandomRepl(BaseSetAssoc):
    type = 'RandomRepl'
    cxx_class = 'RandomRepl'
    cxx_header = "mem/cache/tags/random_repl.hh"

class FALRU(BaseTags):
    type = 'FALRU'
    cxx_class = 'FALRU'
    cxx_header = "mem/cache/tags/fa_lru.hh"
