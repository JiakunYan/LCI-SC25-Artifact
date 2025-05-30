//  Copyright (c) 2023 Jiakun Yan
//
//  SPDX-License-Identifier: BSL-1.0
//  Distributed under the Boost Software License, Version 1.0. (See accompanying
//  file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#pragma once

#include <hpx/config.hpp>

#if defined(HPX_HAVE_NETWORKING) && defined(HPX_HAVE_PARCELPORT_LCW)

#include <hpx/modules/lcw_base.hpp>
#include <hpx/parcelport_lcw/parcelport_lcw.hpp>

namespace hpx::parcelset::policies::lcw {
    static inline void yield_k(int &k, int max_k = 32) {
        if (++k >= max_k) {
            k = 0;
            if (hpx::threads::get_self_id() !=
                hpx::threads::invalid_thread_id)
                hpx::this_thread::yield();
        }
    }
}    // namespace hpx::parcelset::policies::lcw

#endif
