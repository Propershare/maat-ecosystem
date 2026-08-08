import type { PrismaClient } from "@prisma/client";

/**
 * Blood organ — persist events for audit and future fan-out (queues can subscribe later).
 */
export class BloodEventBus {
  constructor(private readonly db: PrismaClient) {}

  async publish(eventType: string, payload: unknown, source = "blood") {
    await this.db.eventLog.create({
      data: { eventType, payload: payload as object, source },
    });
  }
}
