import "vitest"

declare module "vitest" {
  interface Assertion<T = any> {
    toBeOk(expected: any): T
    toBeErr(expected: any): T
    toBeSome(expected: any): T
  }
}
