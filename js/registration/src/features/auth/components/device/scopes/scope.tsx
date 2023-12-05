import { Scope } from "#src/features/auth/types/AccountInfo"

export const scopeDescriptions = {
  [Scope.admin]: "Admin access",
  [Scope.cart]: "Create and checkout carts",
  [Scope.checkout]: "View and search checkouts",
  [Scope.event]: "View event information",
  [Scope.registration]: "View and search registrations",
  [Scope.registrationEdit]: "Edit registrations",
  [Scope.selfService]: "View and manage your own registrations",
} satisfies Record<string, string>
