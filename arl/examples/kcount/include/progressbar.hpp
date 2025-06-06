#ifndef __PROGRESSBAR_HPP
#define __PROGRESSBAR_HPP

#include "sys/stat.h"
#include <chrono>
#include <iostream>
#include <iomanip>
#include <fstream>

#include "arl.hpp"

using std::string;


#define RANK_FOR_PROGRESS 0

extern bool _show_progress;

class ProgressBar {
private:
  int64_t ticks = 0;
  int64_t prev_ticks = 0;
  int64_t ten_perc = 0;
  int64_t total_ticks = 0;
  const int64_t bar_width;
  const int64_t prefix_width;
  const string prefix_str = "";
  const char complete_char = '=';
  const char incomplete_char = ' ';
  const std::chrono::steady_clock::time_point start_time = std::chrono::steady_clock::now();
  std::chrono::steady_clock::time_point prev_time;
  std::istream *infile = nullptr;

public:
  ProgressBar(int64_t total, string prefix = "", int pwidth = 20,
              int width = 50, char complete = '=', char incomplete = ' ')
    : total_ticks{total}
    , prefix_str{prefix}
    , prefix_width{pwidth}
    , bar_width{width}
    , complete_char{complete}
    , incomplete_char{incomplete} {
      if (_show_progress) {
        if (arl::rank_me() == RANK_FOR_PROGRESS) {
          ten_perc = total / 10;
          if (ten_perc == 0) ten_perc = 1;
          std::cout << KLGREEN << "* " << prefix_str << "... " << std::flush;
          prev_time = start_time;
        }
      }
    }

  ProgressBar(const string &fname, std::istream *infile, string prefix = "", int pwidth = 20, int width = 50,
              char complete = '=', char incomplete = ' ')
    : infile{infile}
    , total_ticks{0}
    , prefix_str{prefix}
    , prefix_width{pwidth}
    , bar_width{width}
    , complete_char{complete}
    , incomplete_char{incomplete} {
      if (_show_progress) {
        if (arl::rank_me() == RANK_FOR_PROGRESS) {
          /*
            struct stat stat_buf;
            stat(fname.c_str(), &stat_buf);
            total_ticks = stat_buf.st_size;
          */
          int64_t sz = get_file_size(fname);
          if (sz < 0) std::cout << KRED << "Could not read the file size for: " << fname << std::flush;
          total_ticks = sz;
          ten_perc = total_ticks / 10;
          if (ten_perc == 0) ten_perc = 1;
          ticks = 0;
          prev_ticks = ticks;
          std::cout << KLGREEN << "* " << (prefix_str + " ") << (fname.substr(fname.find_last_of("/\\") + 1) + " " + get_size_str(sz))
                    << "... " << std::flush;
          prev_time = start_time;
        }
      }
  }

  ~ProgressBar() {
    //done();
  }

  void display(bool is_last = false) {
    if (_show_progress) {
      if (arl::rank_me() != RANK_FOR_PROGRESS) return;
      if (total_ticks == 0) return;
      float progress = (float) ticks / total_ticks;
      int pos = (int) (bar_width * progress);

      std::chrono::steady_clock::time_point now = std::chrono::steady_clock::now();
      auto time_elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - start_time).count();
      auto time_delta = std::chrono::duration_cast<std::chrono::milliseconds>(now - prev_time).count();
      //if (time_delta < 1000) return;
      if (prev_time == start_time) std::cout << std::endl;
      double free_mem = get_free_mem_gb();
      std::cout << std::setprecision(2) << std::fixed;
      std::cout << "  " << int(progress * 100.0) << "% " << (float(time_elapsed) / 1000.0) << "s "
                << (float(time_delta) / 1000.0) << "s " << free_mem << "GB" << std::flush << std::endl;
      prev_time = now;
    }
  }

  void done(bool collective = false) {
    if (_show_progress) {
      //display(true);
      std::chrono::steady_clock::time_point now = std::chrono::steady_clock::now();
      auto time_elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - start_time).count();
//      DBG("Time ", prefix_str, ": ", (double)time_elapsed / 1000, "\n");
      if (collective) {
        double max_time = (double)arl::reduce_one(time_elapsed, arl::op_max(), RANK_FOR_PROGRESS) / 1000;
        double tot_time = (double)arl::reduce_one(time_elapsed, arl::op_plus(), RANK_FOR_PROGRESS) / 1000;
        double av_time = tot_time / arl::rank_n();
        if (arl::rank_me() == RANK_FOR_PROGRESS) {
          std::cout << std::setprecision(2) << std::fixed;
          std::cout << "  Average " << av_time << " max " << max_time << " (balance " <<  (max_time == 0.0 ? 1.0 : (av_time / max_time))
                    << ")"<< KNORM << std::endl;
        }
      } else {
        if (arl::rank_me() == RANK_FOR_PROGRESS) {
          std::cout << std::setprecision(2) << std::fixed;
          std::cout << "  Elapsed " << (double) time_elapsed / 1000 << KNORM << std::endl;
        }
      }
    }
  }

  bool update(int64_t new_ticks = -1) {
    if (_show_progress) {
      if (total_ticks == 0) return false;
      if (new_ticks != -1) ticks = new_ticks;
      else if (infile) ticks = infile->tellg();
      else ticks++;
      if (ticks - prev_ticks > ten_perc) {
        display();
        prev_ticks = ticks;
        return true;
      }
    }
    return false;
  }

};

#endif //__PROGRESSBAR_HPP
