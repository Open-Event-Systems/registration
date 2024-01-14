import { Scope } from "#src/features/auth/types/AccountInfo"

export const scopeDescriptions = {
  [Scope.cart]: "Create and checkout carts",
  [Scope.selfService]: "View and manage your own registrations",
  [Scope.event]: "View event configuration",
  [Scope.checkIn]: "Check in registrations",
  [Scope.registration]: "View and search registrations",
  [Scope.registrationAction]: "Use registration actions",
  [Scope.checkout]: "View and search checkouts",
  [Scope.registrationEdit]: "Create and edit registrations",
  [Scope.queue]: "View/manage the queue",
  [Scope.admin]: "Admin access",
} satisfies Record<string, string>
