/**
 * A result and a function to get the next set of results.
 */
export type PaginatedResult<T> = [T, NextFunc<T> | null]

/**
 * Function to get the next set of results in a paginated list.
 */
export type NextFunc<T> = () => Promise<PaginatedResult<T>>
