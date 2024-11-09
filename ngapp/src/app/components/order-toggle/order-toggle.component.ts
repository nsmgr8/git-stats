import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-order-toggle',
  templateUrl: './order-toggle.component.html',
  styleUrl: './order-toggle.component.css',
  standalone: true,
})
export class OrderToggleComponent {
  @Input() show = false;
  @Input() direction = 1;
}
