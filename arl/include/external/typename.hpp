//
// Created by Jiakun Yan on 3/6/20.
//

#ifndef TESTSHOP_TYPENAME_HPP
#define TESTSHOP_TYPENAME_HPP

#include <string>
#include <string_view>

template<class T>
constexpr std::string_view type_name() {
  using namespace std;
#ifdef __clang__
  string_view p = __PRETTY_FUNCTION__;
  return string_view(p.data() + 34, p.size() - 34 - 1);
#elif defined(__GNUC__)
  string_view p = __PRETTY_FUNCTION__;
#if __cplusplus < 201402
  return string_view(p.data() + 36, p.size() - 36 - 1);
#else
  return string_view(p.data() + 49, p.find(';', 49) - 49);
#endif
#elif defined(_MSC_VER)
  string_view p = __FUNCSIG__;
  return string_view(p.data() + 84, p.size() - 84 - 7);
#endif
}

template<typename T, typename U, typename... Args>
std::string type_name() {
  using namespace std;
  return string(type_name<T>()) + " " + string(type_name<U, Args...>());
}

#endif//TESTSHOP_TYPENAME_HPP
