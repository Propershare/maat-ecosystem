import { describe, it, expect } from "vitest";
import { enforceLDAPPolicy, getMaatRoleFromLDAPGroups } from "./ldap-policy";
import { isResourceAccessible } from "./three-ring";

describe("getMaatRoleFromLDAPGroups", () => {
  it("prefers outer-ring when admins present", () => {
    expect(getMaatRoleFromLDAPGroups(["middle-ring", "admins"])).toBe("outer-ring");
  });
  it("uses middle-ring when no outer", () => {
    expect(getMaatRoleFromLDAPGroups(["middle-ring"])).toBe("middle-ring");
  });
  it("defaults to inner-ring when unknown groups", () => {
    expect(getMaatRoleFromLDAPGroups(["some-other"])).toBe("inner-ring");
  });
});

describe("enforceLDAPPolicy", () => {
  it("denies write for inner-ring user", () => {
    const d = enforceLDAPPolicy(
      { action: "write", resource: "jarvis/monetization/x" },
      { uid: "u1", groups: ["inner-ring"] },
    );
    expect(d.allowed).toBe(false);
    expect(d.maatRole).toBe("inner-ring");
  });
  it("allows read for inner-ring on governed read", () => {
    const d = enforceLDAPPolicy(
      { action: "read", resource: "jarvis/maat-graphs/x" },
      { uid: "u1", groups: ["inner-ring"] },
    );
    expect(d.allowed).toBe(true);
  });
  it("allows write for outer-ring", () => {
    const d = enforceLDAPPolicy(
      { action: "write", resource: "maatlangchain/foo" },
      { uid: "u2", groups: ["agents"] },
    );
    expect(d.allowed).toBe(true);
    expect(d.maatRole).toBe("outer-ring");
  });
});

describe("isResourceAccessible", () => {
  it("inner-ring path prefix matches canon tree", () => {
    expect(isResourceAccessible("inner-ring", "jarvis/maat-graphs/model.json")).toBe(true);
    expect(isResourceAccessible("inner-ring", "jarvis/monetization/x")).toBe(false);
  });
  it("outer-ring reaches monetization prefix", () => {
    expect(isResourceAccessible("outer-ring", "jarvis/monetization/app")).toBe(true);
  });
});
