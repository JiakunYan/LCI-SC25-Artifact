#include "arl.hpp"
#include <queue>
#include <mutex>
#include <thread>

bool thread_run = true;

size_t issued;
size_t received;
size_t req_num;
size_t rep_num;
const size_t max_payload_size = 64 * 1024 + 1; // 64KiB
char payload[max_payload_size];
size_t payload_size;

void empty_handler(gex_Token_t token, void *buf, size_t nbytes, gex_AM_Arg_t id) {
  {

  }
  gex_AM_ReplyMedium(token, rep_num, buf, nbytes, GEX_EVENT_NOW, 0, id);
}

void reply_handler(gex_Token_t token, void *buf, size_t nbytes, gex_AM_Arg_t id) {
  received++;
}

void worker(int id) {
  size_t num_ams = 10000;
//  arl::SimpleTimer timer;

  srand48(arl::backend::rank_me());
  arl::backend::barrier();
  auto begin = std::chrono::high_resolution_clock::now();

  for (size_t i = 0; i < num_ams; i++) {
    size_t remote_proc = lrand48() % arl::backend::rank_n();
//    size_t remote_proc = lrand48() % (arl::backend::rank_n() - 1);
//    if (remote_proc >= arl::backend::rank_me()) {
//      remote_proc++;
//    }

    issued++;
    int rv = gex_AM_RequestMedium(arl::backend::internal::tm, remote_proc, req_num, payload, payload_size, GEX_EVENT_NOW, 0, id);
  }

  while (received < issued) {
    gasnet_AMPoll();
  }
  arl::backend::barrier();
  auto end = std::chrono::high_resolution_clock::now();
  double duration_s = std::chrono::duration<double>(end - begin).count();

  double bandwidth_node_s = payload_size * num_ams * 32 / duration_s;
  arl::proc::print("Node single-direction bandwidth = %.3lf MB/s (duration %lf s)\n", bandwidth_node_s / 1e6, duration_s);
}

int main() {
  arl::backend::init(2048);

  payload_size = std::min(
          gex_AM_MaxRequestMedium(arl::backend::internal::tm,GEX_RANK_INVALID,GEX_EVENT_NOW,0,1),
          gex_AM_MaxReplyMedium  (arl::backend::internal::tm,GEX_RANK_INVALID,GEX_EVENT_NOW,0,1)
  );
  payload_size = std::min(max_payload_size, payload_size);
  payload_size = payload_size;
  if (arl::backend::rank_me() == 0)
    std::printf("Maximum medium payload size is %lu\n", payload_size);
#ifdef GASNETC_GNI_MULTI_DOMAIN
  if (arl::backend::rank_me() == 0)
    std::printf("enable gasnet multi domain\n");
#endif
  size_t max_args = gex_AM_MaxArgs();
  size_t handler_num = GEX_AM_INDEX_BASE;
  req_num = handler_num++;
  rep_num = handler_num++;

  gex_AM_Entry_t entry[2];
  entry[0].gex_index = req_num;
  entry[0].gex_fnptr = (gex_AM_Fn_t) empty_handler;
  entry[0].gex_flags = GEX_FLAG_AM_MEDIUM | GEX_FLAG_AM_REQUEST;
  entry[0].gex_nargs = 1;

  entry[1].gex_index = rep_num;
  entry[1].gex_fnptr = (gex_AM_Fn_t) reply_handler;
  entry[1].gex_flags = GEX_FLAG_AM_MEDIUM | GEX_FLAG_AM_REPLY;
  entry[1].gex_nargs = 1;

  int rv = gex_EP_RegisterHandlers(arl::backend::internal::ep, entry, 2);

  worker(0);

  arl::backend::finalize();
  return 0;

}
