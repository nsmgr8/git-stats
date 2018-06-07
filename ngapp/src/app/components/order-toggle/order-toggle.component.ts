import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-order-toggle',
  templateUrl: './order-toggle.component.html',
  styleUrls: ['./order-toggle.component.styl']
})
export class OrderToggleComponent {
    @Input() show = false;
    @Input() direction = 1;
}
