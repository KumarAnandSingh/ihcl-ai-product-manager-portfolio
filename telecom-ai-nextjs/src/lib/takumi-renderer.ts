import { Renderer } from "@takumi-rs/core";
import { container, text } from "@takumi-rs/helpers";

export class TakumiRenderer {
  private renderer: Renderer;

  constructor() {
    this.renderer = new Renderer({
      fonts: [],
      persistentImages: []
    });
  }

  async generatePlanComparisonCard(plans: any[]) {
    const layout = container({
      width: 800,
      height: 400,
      backgroundColor: 0xf8fafc,
      children: [
        // Header
        container({
          width: 800,
          height: 80,
          backgroundColor: 0x3b82f6,
          children: [
            text("📋 Plan Comparison", {
              fontSize: 24,
              color: 0xffffff,
              x: 20,
              y: 25,
            })
          ]
        }),
        // Plan cards container
        container({
          width: 800,
          height: 320,
          backgroundColor: 0xf8fafc,
          x: 0,
          y: 80,
          children: plans.slice(0, 2).map((plan, index) => 
            container({
              width: 300,
              height: 220,
              backgroundColor: 0xffffff,
              borderColor: 0xe2e8f0,
              borderWidth: 2,
              x: 50 + (index * 350),
              y: 40,
              children: [
                text(plan.name, {
                  fontSize: 20,
                  color: 0x1e293b,
                  x: 20,
                  y: 20,
                }),
                text(plan.price, {
                  fontSize: 20,
                  color: 0x059669,
                  x: 20,
                  y: 60,
                }),
                ...plan.features.slice(0, 3).map((feature: string, featureIndex: number) =>
                  text(`✓ ${feature}`, {
                    fontSize: 16,
                    color: 0x64748b,
                    x: 20,
                    y: 100 + (featureIndex * 25),
                  })
                )
              ]
            })
          )
        })
      ],
    });

    const imageBuffer = await this.renderer.renderAsync(layout, {
      width: 800,
      height: 400,
      format: "WebP" as any,
    });

    // Convert to base64
    const base64 = Buffer.from(imageBuffer).toString('base64');
    return `data:image/webp;base64,${base64}`;
  }

  async generateAccountSummaryCard(data: any) {
    const layout = container({
      width: 600,
      height: 300,
      backgroundColor: 0xf8fafc,
      children: [
        // Header
        container({
          width: 600,
          height: 60,
          backgroundColor: 0x6366f1,
          children: [
            text("📊 Account Summary", {
              fontSize: 20,
              color: 0xffffff,
              x: 20,
              y: 18,
            })
          ]
        }),
        // Content
        container({
          width: 600,
          height: 240,
          backgroundColor: 0xf8fafc,
          x: 0,
          y: 60,
          children: [
            text(`💰 Balance: ${data.balance || '₹156.50'}`, {
              fontSize: 16,
              color: 0x1e293b,
              x: 30,
              y: 30,
            }),
            text(`📶 Data Left: ${data.data_left || '2.5 GB'}`, {
              fontSize: 16,
              color: 0x1e293b,
              x: 30,
              y: 70,
            }),
            text(`📅 Validity: ${data.validity || '15 days'}`, {
              fontSize: 16,
              color: 0x1e293b,
              x: 30,
              y: 110,
            })
          ]
        })
      ],
    });

    const imageBuffer = await this.renderer.renderAsync(layout, {
      width: 600,
      height: 300,
      format: "WebP" as any,
    });

    const base64 = Buffer.from(imageBuffer).toString('base64');
    return `data:image/webp;base64,${base64}`;
  }
}

export const takumiRenderer = new TakumiRenderer();