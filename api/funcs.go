package main

func In[T comparable](xs []T, y T) bool {
	for _, x := range xs {
		if x == y {
			return true
		}
	}
	return false
}

func Map[T, R any](xs []T, f func(T) R) []R {
	ret := make([]R, 0, len(xs))
	for i := range xs {
		ret = append(ret, f(xs[i]))
	}
	return ret
}
